"""Compile-time checks for admin Jinja templates (no DB)."""


def test_admin_runs_template_compiles():
    """Regression: duplicate {% endif %} in runs.html caused TemplateSyntaxError on /runs."""
    from organic_market_agent.admin import create_app

    app = create_app()
    with app.app_context():
        app.jinja_env.get_template("admin/runs.html")
