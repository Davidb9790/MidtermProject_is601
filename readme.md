IS601 – Modular Python Calculator
1. Introduction
This project implements a modular, extensible command‑line calculator developed in Python.
The application demonstrates the integration of multiple software engineering design patterns, robust input validation, persistent data storage, and automated testing practices.
It is designed to serve as a maintainable and scalable example of professional software architecture within an academic context.

2. System Overview
The calculator supports a variety of arithmetic operations, maintains a persistent calculation history, and provides undo/redo functionality.
The system architecture incorporates the following design patterns:

Strategy Pattern: Each arithmetic operation is encapsulated within its own class, enabling interchangeable execution strategies.
Factory Pattern: A centralized factory constructs operation objects based on user‑provided identifiers.
Observer Pattern: Observers monitor calculation events, enabling automatic logging and optional auto‑saving.
Memento Pattern: The calculator preserves historical states to support undo and redo operations.

The application uses Python’s Decimal type to ensure numerical precision and employs pandas for structured history storage.

3. Installation Instructions
3.1 Clone the Repository
git clone <your-repository-url>
cd <project-directory>

3.2 Create and Activate a Virtual Environment
python3 -m venv venv
source venv/bin/activate (macOS/Linux)
venv\Scripts\activate (Windows)

3.3 Install Dependencies
pip install -r requirements.txt

5. Usage Guide
5.1 Launching the Calculator
Execute the REPL interface using:
python -m app.calculator_repl

5.2 Supported Commands
add — Add two numbers
subtract — Subtract the second operand from the first
multiply — Multiply two numbers
divide — Divide the first operand by the second
power — Compute a raised to the power of b
root — Compute the b‑th root of a
modulus — Compute a modulo b
integer_division — Perform floor division
percentage — Compute (a × b) / 100
absolute_difference — Compute |a − b|
history — Display calculation history
clear — Clear all stored history
undo — Revert the most recent calculation
redo — Reapply the most recently undone calculation
save — Save history to persistent storage
load — Load history from persistent storage
exit — Terminate the application

5.4 Viewing Calculator History
The calculator stores every completed operation in a persistent history log.
You can view this history at any time by entering the history command.

Example:

Enter command: history
1: 5 + 3 = 8
2: 10 / 2 = 5
3: 7 * 4 = 28

If no history exists, the system displays:
No history available.

5.5 Undo and Redo
The calculator supports undo and redo operations using an internal history state system.
These commands allow you to revert or reapply previous calculations without re‑entering values.

Undo
Reverts the most recent calculation.
If there is no previous calculation to undo, the system notifies you.

Example:
Enter command: undo
Most recent calculation undone.

Redo
Reapplies the most recently undone calculation.
If there is nothing to redo, the system notifies you.

Example:
Enter command: redo
Last undone calculation restored.

5.6 Saving Calculation History
The calculator allows you to save your calculation history to persistent storage.
This ensures that your past operations remain available even after restarting the program.

Example:
Enter command: save
History successfully saved.

If saving fails, the system will notify you.

5.7 Loading Calculation History
You can load previously saved history at any time.
This restores your past calculations into the current session.

Example:
Enter command: load
History successfully loaded.

If no saved history exists, the system displays:
No saved history found.

5.8 Clearing Calculation History
The clear command removes all stored calculations from the current session.
This action does not delete saved history on disk unless you overwrite it later.

Example:
Enter command: clear
History cleared.

5.9 Exiting the Application
To close the calculator, enter the exit command.
The program will terminate immediately.

Example:
Enter command: exit
Goodbye.

6. Testing and Quality Assurance
This project includes automated unit tests to ensure correctness, reliability, and maintainability.
Tests cover:

Arithmetic operations
Input validation
History management
Undo and redo functionality
Factory and strategy behavior
Error handling

To run the test suite, use your preferred Python test runner (for example, pytest).

7. Project Structure
The project follows a modular architecture with clear separation of concerns.
Typical components include:

Operation classes
Factory for operation creation
History manager
Memento system for undo/redo
REPL interface
Utility modules
Test suite

This structure supports scalability, readability, and ease of maintenance.

8. Conclusion
This modular Python calculator demonstrates clean software design, extensibility, and robust state management.
It serves as a practical example of applying design patterns and testing practices in a real‑world Python application.