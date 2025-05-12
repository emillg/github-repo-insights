import matplotlib.pyplot as plt


def plot_line_chart(data_series, title, ylabel, labels, filename):
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


def plot_bar_chart(categories, values, title, xlabel, ylabel, filename):
    sorted_data = sorted(zip(values, categories), reverse=True)
    values, categories = zip(*sorted_data)

    plt.style.use("seaborn-v0_8-pastel")
    plt.figure(figsize=(12, 6))

    bars = plt.barh(range(len(categories)), values, color="skyblue")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.yticks(range(len(categories)), [""] * len(categories))

    for bar, category in zip(bars, categories):
        plt.text(
            bar.get_width() + 5,
            bar.get_y() + bar.get_height() / 2,
            category,
            va="center",
            fontsize=9,
            color="black"
        )

    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
