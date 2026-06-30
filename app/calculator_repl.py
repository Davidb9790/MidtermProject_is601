########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory

from colorama import Fore, Style, init
init(autoreset=True)

def calculator_repl():  # pragma: no cover
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(Fore.MAGENTA + "Calculator started. Type 'help' for commands." + Style.RESET_ALL)

        while True:
            try:
                # Prompt the user for a command
                command = input(Fore.CYAN + "\nEnter command: " + Style.RESET_ALL).lower().strip()  # pragma: no cover

                # Handle empty input FIRST
                if command == "":
                    print(Fore.RED + "Error: No command entered. Type 'help' for a list of valid commands." + Style.RESET_ALL)
                    continue  # pragma: no cover

                # HELP
                if command == 'help':
                    print("\nAvailable commands:")
                    print("  add, subtract, multiply, divide, power, root, modulus, integer_division, percentage, absolute_difference - Perform calculations")
                    print("  history - Show calculation history")
                    print("  clear - Clear calculation history")
                    print("  undo - Undo the last calculation")
                    print("  redo - Redo the last undone calculation")
                    print("  save - Save calculation history to file")
                    print("  load - Load calculation history from file")
                    print("  exit - Exit the calculator")
                    continue  # pragma: no cover

                # EXIT
                elif command == 'exit':
                    try:
                        calc.save_history()
                        print(Fore.CYAN + "History saved successfully." + Style.RESET_ALL)
                    except Exception as e:
                        print(f"Warning: Could not save history: {e}")
                    print(Fore.MAGENTA + "Goodbye!" + Style.RESET_ALL)
                    break  # pragma: no cover

                # HISTORY
                elif command == 'history':
                    history = calc.show_history()
                    if not history:
                        print(Fore.MAGENTA + "No calculations in history" + Style.RESET_ALL)
                    else:
                        print(Fore.MAGENTA + "\nCalculation History:" + Style.RESET_ALL)
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue  # pragma: no cover

                # CLEAR
                elif command == 'clear':
                    calc.clear_history()
                    print(Fore.MAGENTA + "History cleared" + Style.RESET_ALL)
                    continue  # pragma: no cover

                # UNDO
                elif command == 'undo':
                    if calc.undo():
                        print(Fore.YELLOW + "Operation undone" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Nothing to undo" + Style.RESET_ALL)
                    continue  # pragma: no cover

                # REDO
                elif command == 'redo':
                    if calc.redo():
                        print(Fore.YELLOW + "Operation redone" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Nothing to redo" + Style.RESET_ALL)
                    continue  # pragma: no cover

                # SAVE
                elif command == 'save':
                    try:
                        calc.save_history()
                        print(Fore.CYAN + "History saved successfully" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"Error saving history: {e}" + Style.RESET_ALL)
                    continue  # pragma: no cover

                # LOAD
                elif command == 'load':
                    try:
                        calc.load_history()
                        print(Fore.CYAN + "History loaded successfully" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"Error loading history: {e}" + Style.RESET_ALL)
                    continue  # pragma: no cover

                # OPERATIONS
                elif command in [
                    'add', 'subtract', 'multiply', 'divide', 'power', 'root',
                    'modulus', 'integer_division', 'percentage', 'absolute_difference'
                ]:

                    # Validate operation exists in factory
                    if command not in OperationFactory._operations:
                        print(Fore.RED + f"Error: Operation '{command}' is not supported." + Style.RESET_ALL)
                        continue  # pragma: no cover

                    try:
                        print("\nEnter numbers (or 'cancel' to abort):")
                        a = input("First number: ")  # pragma: no cover
                        if a.lower() == 'cancel':
                            print("Operation cancelled")
                            continue  # pragma: no cover

                        b = input("Second number: ")  # pragma: no cover
                        if b.lower() == 'cancel':
                            print("Operation cancelled")
                            continue  # pragma: no cover

                        # Validate numeric input
                        try:
                            Decimal(a)
                            Decimal(b)
                        except Exception:
                            print(Fore.RED + "Error: Both inputs must be valid numbers." + Style.RESET_ALL)
                            continue  # pragma: no cover

                        # Create operation instance
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform calculation
                        result = calc.perform_operation(a, b)

                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(Fore.GREEN + f"\nResult: {result}" + Style.RESET_ALL)

                    except (ValidationError, OperationError) as e:
                        print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                    except Exception as e:
                        print(Fore.RED + f"Unexpected error: {e}" + Style.RESET_ALL)
                    continue  # pragma: no cover

                # UNKNOWN COMMAND — FINAL CATCH
                else:
                    print(Fore.RED + f"Unknown command: '{command}'" + Style.RESET_ALL)
                    continue

            except KeyboardInterrupt:  # pragma: no cover
                print(Fore.YELLOW + "\nOperation cancelled" + Style.RESET_ALL)
                continue

            except EOFError:  # pragma: no cover
                print(Fore.YELLOW + "\nInput terminated. Exiting..." + Style.RESET_ALL)
                break

            except Exception as e:  # pragma: no cover
                print(Fore.RED + f"Error: {e}" + Style.RESET_ALL)
                continue

    except Exception as e:  # pragma: no cover
        print(Fore.RED + f"Fatal error: {e}" + Style.RESET_ALL)
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise
