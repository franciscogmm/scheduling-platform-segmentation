import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
def plot_segments_xyz_scatter(pdf, x, y, z, hue_col, alpha=0.5, figsize=(6, 6)):
    # axes instance
    fig = plt.figure(figsize=figsize)
    ax = Axes3D(fig, auto_add_to_figure=False)
    fig.add_axes(ax)

    # plot
    sc = ax.scatter(
        pdf[x],
        pdf[y],
        pdf[z],
        s=40,
        c=pdf[hue_col],
        marker='o',
        # cmap=cmap,
        alpha=alpha,
    )
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_zlabel(z)

    # legend
    plt.legend(*sc.legend_elements(), bbox_to_anchor=(1.05, 1), loc=2)