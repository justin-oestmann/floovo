# Floovo 🌟

Floovo is a modern web application designed to enhance your media browsing experience. This README will guide you through the installation process and show you how to use the application effectively.

> **Note**: This project was entirely developed and created using **GitHub Copilot**. 🤖✨

---

## 🚀 Installation

Follow these steps to set up Floovo on your local machine:

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-repo/floovo.git
   cd floovo
   ```

2. **Install Python and Dependencies**  
   Make sure you have [Python 3.10+](https://www.python.org/) installed. Then create a virtual environment and install the required dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the Application**  
   Start the Flask development server:
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5000`.

---

## 🛠️ Libraries and Frameworks

Floovo uses the following libraries and frameworks:

- **Backend**:  
  - [Flask](https://flask.palletsprojects.com/) for server-side logic.
  - [Pillow](https://python-pillow.org/) for image processing.
  - [ImageHash](https://pypi.org/project/ImageHash/) for image similarity analysis.

- **Frontend**:  
  - [Bootstrap](https://getbootstrap.com/) for responsive design.
  - [Bootstrap Icons](https://icons.getbootstrap.com/) for icons.

---

## 🎨 Customization

You can modify the styles in the `static/style.css` file. For example, the navbar logo margin is defined as:
```css
.navbar-brand img {
    margin-right: 10px;
}
```

---

## 🧑‍💻 Usage

1. Open the application in your browser (`http://localhost:5000`).
2. Browse through the media content.
3. Use the upload feature to add files and start sorting.
4. Enjoy the seamless experience! 🎉

---

## 📂 File Structure

- `static/style.css`: Custom CSS styles.
- `app.py`: Backend server logic.
- `templates/`: HTML templates.

---

## 🤝 Contributing

We welcome contributions! Feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Enjoy using Floovo! 💻✨