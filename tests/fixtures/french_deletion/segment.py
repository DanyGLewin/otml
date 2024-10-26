from src.grammar.base_segment import BaseSegment


class Segment(BaseSegment):
    cons: bool
    high: bool
    stop: bool
    son: bool
    voice: bool
    labial: bool
    liquid: bool
