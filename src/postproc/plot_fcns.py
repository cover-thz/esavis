

import numpy as np
import matplotlib.pyplot as plt
def plot_pixel_power(pix_pwr_lin, range_lut_cm, show=True):
    title = "Power spectrum of a single pixel in dB"
    pix_pwr_db = 10*np.log10(pix_pwr_lin)
    fig, ax = plt.subplots()
    plt.plot(range_lut_cm, pix_pwr_db, "r")
    plt.xlabel("range in cm")
    plt.ylabel("power in dB")
    plt.title(title)
    #fig.set_figheight(6)
    fig.tight_layout()
    if show:
        plt.show()
    else:
        plt.draw()




def plot_img_vals(thz_image_vals, coarse_az_array, coarse_el_array, 
    color_min, color_max, title, show=True):
    """
    plots image values, output of tier 3 post processing 
    """
    az_min = coarse_az_array.min()
    az_max = coarse_az_array.max()

    el_min = coarse_el_array.min()
    el_max = coarse_el_array.max()

    colormap_val = "jet_r"
    fig, ax = plt.subplots()

    plt.imshow(thz_image_vals.T, extent=[az_min, az_max, el_min, el_max],
                                    aspect='equal', origin='lower', 
                                    cmap=colormap_val, vmin=color_min, 
                                    vmax=color_max)
    plt.gca().invert_xaxis()  # Reverse x-axis
    plt.gca().invert_yaxis()  # Reverse y-axis
    plt.colorbar(label='range (cm)')
    plt.xlabel('interp. Az encoder vals')
    plt.ylabel('interp. El encoder vals from start')
    plt.title(title)
    fig.set_figheight(6)
    fig.tight_layout()
    if show:
        plt.show()
    else:
        plt.draw()


