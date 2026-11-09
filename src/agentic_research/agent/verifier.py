"""Citation verification that keeps unsupported claims out of the report (#6).

A claim survives only if (1) it cites something, (2) every cited number is a
document that was actually retrieved, and (3) the cited text supports it.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from ..contracts import Claim, Draft, Hit
from ..ports import LLMPort


@dataclass(frozen=True)
class Verification:
    supported: list[Claim]
    issues: list[str] = field(default_factory=list)
    no_citation: int = 0
    invalid_citation: int = 0
    unsupported: int = 0

    @property
    def ok(self) -> bool:
        return not self.issues

    def stats(self, total_claims: int) -> dict[str, int]:
        return {
            "claims": total_claims,
            "supported": len(self.supported),
            "no_citation": self.no_citation,
            "invalid_citation": self.invalid_citation,
            "unsupported": self.unsupported,
        }


def verify(draft: Draft, evidence: Sequence[Hit], llm: LLMPort) -> Verification:
    issues: list[str] = []
    checkable: list[tuple[int, Claim]] = []
    no_citation = invalid_citation = 0
    for number, claim in enumerate(draft.claims, start=1):
        if not claim.citations:
            issues.append(f"주장 {number}: 인용이 없다")
            no_citation += 1
            continue
        unknown = [c for c in claim.citations if not 1 <= c <= len(evidence)]
        if unknown:
            issues.append(
                f"주장 {number}: 검색되지 않은 문서 번호 {unknown}를 인용했다"
            )
            invalid_citation += 1
            continue
        cited = list(dict.fromkeys(claim.citations))
        checkable.append((number, claim.model_copy(update={"citations": cited})))

    verdicts = llm.check_support(
        [
            (
                claim.text,
                "\n".join(evidence[c - 1].record.text for c in claim.citations),
            )
            for _, claim in checkable
        ]
    )
    supported: list[Claim] = []
    unsupported = 0
    for (number, claim), verdict in zip(checkable, verdicts, strict=True):
        if verdict:
            supported.append(claim)
        else:
            issues.append(f"주장 {number}: 인용한 문서가 주장을 뒷받침하지 않는다")
            unsupported += 1
    return Verification(
        supported=supported,
        issues=issues,
        no_citation=no_citation,
        invalid_citation=invalid_citation,
        unsupported=unsupported,
    )
