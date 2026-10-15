from dataclasses import dataclass, field, asdict


@dataclass
class Role:
    source: str           # reed, adzuna, freelancer, upwork, ziprecruiter, email:<sender>
    source_id: str        # stable id within the source
    title: str
    url: str
    company: str = ""
    location: str = ""
    remote: bool = False
    rate: str = ""        # human readable, empty if not shown
    rate_shown: bool = False
    contract_type: str = ""   # contract / permanent / freelance / unknown
    description: str = ""
    posted: str = ""
    extra: dict = field(default_factory=dict)
    # set by match.classify
    verdict: str = ""     # strong / maybe / drop
    reason: str = ""

    @property
    def key(self) -> str:
        return f"{self.source}:{self.source_id}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["key"] = self.key
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Role":
        d = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**d)
