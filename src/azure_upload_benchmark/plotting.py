"""Plot generation for benchmark results (heatmaps, line plots, 3-D surface)."""

import os

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def generate_plots(results: list[dict], output_dir: str) -> None:
    """Generate heatmap, line, and surface plots from benchmark results.

    Silently returns if *matplotlib* / *numpy* are not installed.
    """
    if not HAS_MATPLOTLIB:
        print(
            "Skipping plot generation (matplotlib/numpy not installed). "
            "Install with: pip install azure-upload-benchmark[plots]"
        )
        return

    os.makedirs(output_dir, exist_ok=True)

    chunk_sizes = sorted({r["chunk_size_mb"] for r in results})
    concurrencies = sorted({r["concurrency"] for r in results})

    throughput_matrix = np.zeros((len(concurrencies), len(chunk_sizes)))
    elapsed_matrix = np.zeros((len(concurrencies), len(chunk_sizes)))

    for r in results:
        ci = concurrencies.index(r["concurrency"])
        csi = chunk_sizes.index(r["chunk_size_mb"])
        throughput_matrix[ci][csi] = r["avg_throughput_mbps"]
        elapsed_matrix[ci][csi] = r["avg_elapsed_s"]

    file_size = results[0]["file_size_mb"]

    _plot_throughput_heatmap(
        throughput_matrix, chunk_sizes, concurrencies, file_size, output_dir
    )
    _plot_time_heatmap(
        elapsed_matrix, chunk_sizes, concurrencies, file_size, output_dir
    )
    _plot_line_plots(results, chunk_sizes, concurrencies, file_size, output_dir)
    _plot_3d_surface(
        throughput_matrix, chunk_sizes, concurrencies, file_size, output_dir
    )


# ── Internal helpers ────────────────────────────────────────────────────


def _plot_throughput_heatmap(matrix, chunk_sizes, concurrencies, file_size, output_dir):
    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(matrix, cmap="YlGn", aspect="auto")
    ax.set_xticks(range(len(chunk_sizes)))
    ax.set_xticklabels([f"{s} MB" for s in chunk_sizes])
    ax.set_yticks(range(len(concurrencies)))
    ax.set_yticklabels(concurrencies)
    ax.set_xlabel("Chunk Size", fontsize=12)
    ax.set_ylabel("Concurrency", fontsize=12)
    ax.set_title(
        f"Upload Throughput (MB/s) — File Size: {file_size:.0f} MB", fontsize=14
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Throughput (MB/s)", fontsize=11)

    for i in range(len(concurrencies)):
        for j in range(len(chunk_sizes)):
            val = matrix[i][j]
            text_color = "white" if val > matrix.max() * 0.7 else "black"
            ax.text(
                j,
                i,
                f"{val:.1f}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=9,
            )

    best_idx = np.unravel_index(matrix.argmax(), matrix.shape)
    ax.add_patch(
        plt.Rectangle(
            (best_idx[1] - 0.5, best_idx[0] - 0.5),
            1,
            1,
            fill=False,
            edgecolor="red",
            linewidth=3,
        )
    )
    best_conc = concurrencies[best_idx[0]]
    best_chunk = chunk_sizes[best_idx[1]]
    best_tp = matrix[best_idx[0]][best_idx[1]]
    ax.text(
        0.02,
        0.98,
        f"Best: chunk={best_chunk}MB, concurrency={best_conc} ({best_tp:.1f} MB/s)",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8),
    )

    fig.tight_layout()
    path = os.path.join(output_dir, "throughput_heatmap.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved: {path}")


def _plot_time_heatmap(matrix, chunk_sizes, concurrencies, file_size, output_dir):
    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(matrix, cmap="YlOrRd_r", aspect="auto")
    ax.set_xticks(range(len(chunk_sizes)))
    ax.set_xticklabels([f"{s} MB" for s in chunk_sizes])
    ax.set_yticks(range(len(concurrencies)))
    ax.set_yticklabels(concurrencies)
    ax.set_xlabel("Chunk Size", fontsize=12)
    ax.set_ylabel("Concurrency", fontsize=12)
    ax.set_title(f"Upload Time (seconds) — File Size: {file_size:.0f} MB", fontsize=14)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Time (s)", fontsize=11)

    for i in range(len(concurrencies)):
        for j in range(len(chunk_sizes)):
            val = matrix[i][j]
            threshold = matrix.min() + (matrix.max() - matrix.min()) * 0.3
            text_color = "white" if val < threshold else "black"
            ax.text(
                j,
                i,
                f"{val:.1f}s",
                ha="center",
                va="center",
                color=text_color,
                fontsize=9,
            )

    best_idx = np.unravel_index(matrix.argmin(), matrix.shape)
    ax.add_patch(
        plt.Rectangle(
            (best_idx[1] - 0.5, best_idx[0] - 0.5),
            1,
            1,
            fill=False,
            edgecolor="blue",
            linewidth=3,
        )
    )

    fig.tight_layout()
    path = os.path.join(output_dir, "upload_time_heatmap.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved: {path}")


def _plot_line_plots(results, chunk_sizes, concurrencies, file_size, output_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    colors = plt.cm.viridis(np.linspace(0, 1, len(chunk_sizes)))
    for idx, cs in enumerate(chunk_sizes):
        concs = []
        tps = []
        for r in sorted(results, key=lambda x: x["concurrency"]):
            if r["chunk_size_mb"] == cs:
                concs.append(r["concurrency"])
                tps.append(r["avg_throughput_mbps"])
        ax1.plot(
            concs,
            tps,
            "o-",
            color=colors[idx],
            label=f"{cs} MB",
            linewidth=2,
            markersize=6,
        )

    ax1.set_xlabel("Concurrency", fontsize=12)
    ax1.set_ylabel("Throughput (MB/s)", fontsize=12)
    ax1.set_title("Throughput vs Concurrency (by Chunk Size)", fontsize=13)
    ax1.legend(title="Chunk Size", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(concurrencies)

    colors2 = plt.cm.plasma(np.linspace(0, 1, len(concurrencies)))
    for idx, conc in enumerate(concurrencies):
        chunks = []
        tps = []
        for r in sorted(results, key=lambda x: x["chunk_size_mb"]):
            if r["concurrency"] == conc:
                chunks.append(r["chunk_size_mb"])
                tps.append(r["avg_throughput_mbps"])
        ax2.plot(
            chunks,
            tps,
            "s-",
            color=colors2[idx],
            label=f"{conc}",
            linewidth=2,
            markersize=6,
        )

    ax2.set_xlabel("Chunk Size (MB)", fontsize=12)
    ax2.set_ylabel("Throughput (MB/s)", fontsize=12)
    ax2.set_title("Throughput vs Chunk Size (by Concurrency)", fontsize=13)
    ax2.legend(title="Concurrency", fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(chunk_sizes)

    fig.suptitle(
        f"Upload Performance Analysis — {file_size:.0f} MB file", fontsize=15, y=1.02
    )
    fig.tight_layout()
    path = os.path.join(output_dir, "throughput_line_plots.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Plot saved: {path}")


def _plot_3d_surface(matrix, chunk_sizes, concurrencies, file_size, output_dir):
    try:
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection="3d")

        X, Y = np.meshgrid(chunk_sizes, concurrencies)
        ax.plot_surface(
            X,
            Y,
            matrix,
            cmap="viridis",
            alpha=0.85,
            edgecolor="gray",
            linewidth=0.3,
        )
        ax.set_xlabel("Chunk Size (MB)", fontsize=11, labelpad=10)
        ax.set_ylabel("Concurrency", fontsize=11, labelpad=10)
        ax.set_zlabel("Throughput (MB/s)", fontsize=11, labelpad=10)
        ax.set_title(
            f"Upload Throughput Surface — {file_size:.0f} MB file", fontsize=14, pad=20
        )
        ax.view_init(elev=25, azim=225)

        path = os.path.join(output_dir, "throughput_surface_3d.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Plot saved: {path}")
    except Exception as e:
        print(f"3D surface plot skipped: {e}")
