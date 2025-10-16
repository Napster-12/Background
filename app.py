from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Flask-Mail configuration
app.config.update(
    MAIL_SERVER='smtp.gmail.com',  # change if using other provider
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='codnellsmall@gmail.com',   # <-- your email
    MAIL_PASSWORD='mrmxmmomvhvfqoee',    # <-- your email password or app password
    MAIL_DEFAULT_SENDER=("Faya Tech", 'codnellsmall@gmail.com')
)
mail = Mail(app)

# Models
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    billing_name = db.Column(db.String(100), nullable=False)
    billing_email = db.Column(db.String(100), nullable=False)
    billing_phone = db.Column(db.String(50))
    billing_address = db.Column(db.String(200))
    billing_city = db.Column(db.String(100))
    billing_postal = db.Column(db.String(20))
    billing_country = db.Column(db.String(50))
    items_json = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending")

    @property
    def items(self):
        return json.loads(self.items_json)

# Initialize DB
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def home():
    return render_template("home.html")  # Your home page

@app.route("/menu")
def menu():
    return render_template("menu.html")  # Your shop page

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/checkout")
def checkout():
    return render_template("checkout.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/order_success")
def order_success():
    return render_template("order_success.html")

# Admin: view all orders
@app.route("/admin/orders")
def admin_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template("admin_orders.html", orders=orders)

# Admin: update order status
@app.route("/admin/update_status/<int:order_id>", methods=["POST"])
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    order.status = new_status
    db.session.commit()
    flash(f"Order #{order.id} status updated to {new_status}", "success")
    return redirect("/admin/orders")

# Admin: send email to client
@app.route("/admin/send_email/<int:order_id>", methods=["POST"])
def send_email(order_id):
    order = Order.query.get_or_404(order_id)
    msg = Message(
        subject=f"Update on your Order #{order.id}",
        sender=app.config["MAIL_USERNAME"],
        recipients=[order.billing_email]
    )
    msg.body = f"""
Hello {order.billing_name},

Your order #{order.id} status is now: {order.status}.

Order Details:
{json.dumps(order.items, indent=2)}

Total: R{order.total}

Thank you for shopping with FAYA Tech!
"""
    mail.send(msg)
    flash(f"Email sent to {order.billing_email}", "success")
    return redirect("/admin/orders")

# Route to save order (triggered by checkout page)
@app.route("/save_order", methods=["POST"])
def save_order():
    data = request.get_json()
    billing = data.get("billing")
    cart = data.get("cart")
    total = data.get("total")
    order = Order(
        billing_name=billing.get("name"),
        billing_email=billing.get("email"),
        billing_phone=billing.get("phone"),
        billing_address=billing.get("address"),
        billing_city=billing.get("city"),
        billing_postal=billing.get("postal"),
        billing_country=billing.get("country"),
        items_json=json.dumps(cart),
        total=total
    )
    db.session.add(order)
    db.session.commit()
    return {"success": True, "order_id": order.id}

if __name__ == "__main__":
    app.run(debug=True)
