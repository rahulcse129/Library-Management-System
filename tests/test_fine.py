import pytest

from app import calculate_fine


@pytest.mark.parametrize(
    ("overdue_days", "expected_fine"),
    [
        (0, 0),
        (5, 25),
        (1, 5),
    ],
)
def test_calculate_fine_for_valid_days(overdue_days, expected_fine):
    assert calculate_fine(overdue_days) == expected_fine


def test_calculate_fine_rejects_negative_days():
    with pytest.raises(ValueError, match="Overdue days cannot be negative"):
        calculate_fine(-1)
