class InvalidOrderStateError(Exception):
    """주문이 기대하는 상태(RESERVED/CONFIRMED 등)가 아닐 때 발생한다.

    ApprovalController(승인/거절)와 ReleaseController(출고)가 공통으로 사용한다.
    """
