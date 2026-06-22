from flask import Flask, Response, redirect, render_template, request, url_for
from prometheus_client import Counter, generate_latest

from db import get_connection

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "todo_app_requests_total",
    "Total number of requests received by the To-Do Flask application",
    ["method", "endpoint"],
)


@app.before_request
def count_request():
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
    ).inc()


@app.route("/")
def home():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()

    if title:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO tasks (title, completed) VALUES (%s, %s)",
            (title, False),
        )

        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for("home"))


@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET completed = NOT completed
        WHERE id = %s
        """,
        (task_id,),
    )

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = %s",
        (task_id,),
    )

    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for("home"))


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
