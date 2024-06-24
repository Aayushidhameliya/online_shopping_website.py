from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import stripe

app = Flask(__name__)
app.secret_key = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['DATABASE'] = 'database.db'

# Stripe configuration
app.config['STRIPE_PUBLIC_KEY'] = 'YOUR_PUBLIC_KEY'
app.config['STRIPE_SECRET_KEY'] = 'YOUR_SECRET_KEY'
stripe.api_key = app.config['STRIPE_SECRET_KEY']

# Database connection
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM products')
        products = cur.fetchall()
        conn.close()
        return render_template('index.html', products=products)
    except sqlite3.Error as e:
        print("Error fetching products:", e)
        flash('Error fetching products.', 'error')
        return render_template('index.html', products=[])

@app.route('/product/<int:id>')
def product(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM products WHERE id=?', (id,))
        product = cur.fetchone()
        conn.close()
        if product:
            return render_template('product.html', product=product)
        else:
            flash('Product not found.', 'error')
            return redirect(url_for('index'))
    except sqlite3.Error as e:
        print("Error fetching product:", e)
        flash('Error fetching product.', 'error')
        return redirect(url_for('index'))

@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        product_id = request.form['product_id']
        product_price = request.form['product_price']

        # Create a PaymentIntent on Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=int(float(product_price) * 100),  # Amount in cents
            currency='usd',
            description='Payment for Product ID: {}'.format(product_id),
            payment_method_types=['card'],
        )

        return render_template('checkout.html', payment_intent_id=payment_intent.id)
    except Exception as e:
        print("Error during checkout:", str(e))
        flash('Error during checkout. Please try again later.', 'error')
        return redirect(url_for('index'))

@app.route('/payment_success')
def payment_success():
    flash('Payment successful! Thank you for your purchase.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
