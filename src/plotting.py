import matplotlib.pyplot as plt


def plot_chart(data_series, title, ylabel, labels, filename):
    plt.style.use("seaborn-v0_8-pastel")
    plt.figure(figsize=(10, 5))

    for (dates, counts), label in zip(data_series, labels):
        plt.plot(dates, counts, marker="o", label=label)

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
