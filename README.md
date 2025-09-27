# Your Project Title

A brief one or two-sentence description of your project. Explain what it does, who it's for, and the main problem it solves.

## ✨ Features

* Connects securely to a MongoDB database.
* Feature 2: Brief description of another key capability.
* Feature 3: And another one.

## 🔧 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need the following software installed on your machine:

* [Python](https://www.python.org/) (v3.8 or later is recommended)
* [Pip](https://pip.pypa.io/en/stable/installation/) (which is typically included with Python)
* [Git](https://git-scm.com/)
* A MongoDB database instance. You can create a free one on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).

### Installation

1.  **Clone the repository**
    ```sh
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    ```

2.  **Navigate into the project directory**
    ```sh
    cd your-repository-name
    ```

3.  **Create and activate a virtual environment (Recommended)**
    *This isolates your project's dependencies.*
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

4.  **Install Python packages**
    ```sh
    pip install -r requirements.txt
    ```

---

## ⚙️ Configuration

This project uses environment variables to handle configuration and keep sensitive data like database credentials secure.

1.  Create a new file named `.env` in the root of your project.
2.  Copy the contents from `.env.example` into your new `.env` file.
3.  Update the values in the `.env` file with your specific configuration.

**⚠️ Important:** The `.env` file should **never** be committed to version control. Make sure your `.gitignore` file includes a line for `.env`.

### Environment Variables

| Variable         | Description                                                                                                                              | Example                                                                                                  |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `MONGODB_URI`    | **Required.** Your full MongoDB connection string, including your username, password, and database name. This is crucial for connecting to the database. | `mongodb+srv://<user>:<password>@cluster-name.mongodb.net/myDatabase?retryWrites=true&w=majority` |
| `OPENAI_API_KEY`      | **Required.** We need OpenAI key for this project                                                                          | 

---

## 🚀 Running the Application

Once you have installed the dependencies and configured your environment variables, you can run the application with the following command:

```sh
flask run