import csv
import matplotlib.pyplot as plt


def plot_voltage_from_csv(csv_file):
    timestamps = []
    voltages = []

    # Read the CSV file
    with open(csv_file, mode="r") as file:
        csvreader = csv.reader(file)
        next(csvreader)  # Skip the header row
        for row in csvreader:
            timestamps.append(float(row[0]))  # Convert timestamp to float
            voltages.append(float(row[1]))  # Convert voltage to float

    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, voltages, label="Voltage over Time", color="b")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.title("Voltage Measurement Over Time")
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    plot_voltage_from_csv("microphone_data.csv")
