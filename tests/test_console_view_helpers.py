from app.views.console_view import summarize_dashboard, stock_bar


def test_summarize_dashboard_counts_totals_correctly():
    samples = [
        {"sample_id": "S-001", "stock": 280},
        {"sample_id": "S-003", "stock": 24},
    ]
    orders = [
        {"order_id": "ORD-0001", "status": "CONFIRMED"},
        {"order_id": "ORD-0002", "status": "REJECTED"},
    ]
    queue = [{"order_id": "ORD-0003"}]

    summary = summarize_dashboard(samples, orders, queue)

    assert summary["sample_count"] == 2
    assert summary["total_stock"] == 304
    assert summary["order_count"] == 2  # REJECTED 포함
    assert summary["queue_count"] == 1


def test_summarize_dashboard_handles_empty_data():
    summary = summarize_dashboard([], [], [])

    assert summary["sample_count"] == 0
    assert summary["total_stock"] == 0
    assert summary["order_count"] == 0
    assert summary["queue_count"] == 0


def test_stock_bar_full_at_or_above_capacity():
    assert stock_bar(280, capacity=200) == "[##########] 100%"
    assert stock_bar(200, capacity=200) == "[##########] 100%"


def test_stock_bar_partial_fill():
    assert stock_bar(24, capacity=200) == "[#.........] 12%"


def test_stock_bar_zero_stock():
    assert stock_bar(0, capacity=200) == "[..........] 0%"
