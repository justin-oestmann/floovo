# Floovo 🌟

Floovo is a modern web application designed to enhance your media browsing experience. This README will guide you through the installation process and show you how to use the application effectively.

> **Note**: This project was entirely developed and created using **GitHub Copilot**. 🤖✨

---

## 🚀 Quick Start (Recommended)

The easiest way to set up and run Floovo is by using the provided `startup.bat` script. Follow these steps:

1. **Download the Repository**  
   Clone or download the repository from [GitHub](https://github.com/justin-oestmann/floovo).

2. **Run the Startup Script**  
   Double-click the `startup.bat` file located in the project folder. The script will:
   - Check if Python is installed.
   - Verify that all required libraries are installed.
   - Ensure the application is up-to-date by pulling the latest changes from the repository.
   - Start the Floovo application.

3. **Access the Application**  
   Open your browser and navigate to `http://localhost:5000`.

---

## 🛠️ Manual Installation

If you prefer to set up Floovo manually, follow these steps:

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/justin-oestmann/floovo.git
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

## 🧑‍💻 Usage

1. Open the application in your browser (`http://localhost:5000`).
2. Browse through the media content.
3. Use the upload feature to add files and start sorting.
4. Enjoy the seamless experience! 🎉

---

## 📂 File Structure

The project structure is as follows:

```
floovo/
├── app.py                # Main application logic
├── requirements.txt      # Python dependencies
├── startup.bat           # Quick start script
├── static/
│   ├── style.css         # Custom CSS styles
│   └── media/            # Uploaded media files
├── templates/
│   ├── base.html         # Base HTML template
│   ├── index.html        # Homepage template
│   ├── upload.html       # File upload page
│   ├── sort.html         # Sorting page for media
│   ├── setup.html        # Folder setup page
│   └── done.html         # Completion page
├── behalten/             # Folder for retained media
├── loeschen/             # Folder for deleted media
└── .gitignore            # Git ignore rules
```

---

## 🤝 Contributing

We welcome contributions! Feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Enjoy using Floovo! 💻✨