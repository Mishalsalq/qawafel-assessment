from streamlit.testing.v1 import AppTest
from pathlib import Path


def test_sample_dashboard_and_upload_empty_state():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run(timeout=60)
    assert not app.exception
    values = {metric.label: metric.value for metric in app.metric}
    assert values["Net invoiced sales"] == "SAR 3,773,090"
    assert values["Overdue incl. VAT"] == "SAR 282,743"
    # Exercise meaningful user actions rather than just importing the module.
    app.selectbox[0].select("CUS-001").run()
    assert not app.exception
    app.radio[0].set_value("Upload fictional invoices").run()
    assert not app.exception
    assert len(app.metric) == 0
    assert any("Upload a fictional" in message.value for message in app.info)
