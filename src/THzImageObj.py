# This file contains the set of image objects that make up what the user sees
# as the THz image on the THzImageTab tab.  Due to the different ways in which
# the plot needs to be viewed, it is actually multiple different objects 
# that are alternately hidden and displayed to make it look like there's 
# just one object that is controlled by the radio buttons in THzImageTab().  
# 
# This functionality is placed in this seperate file to make the code cleaner 
# more concise and easier to understand
#

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt, QObject, Signal
import PySide6
from math import nan
import copy
import numpy as np
import math
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import matplotlib
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (
     QHBoxLayout,
     QStackedWidget,)


##############################################################################
##############################################################################

class MyViewBox(pg.ViewBox):
    def __init__(s, click_callback=None, *args, **kwargs):
        s.click_callback = click_callback
        super().__init__(*args, **kwargs)

    def mouseClickEvent(s, ev):
        if ev.button() == QtCore.Qt.RightButton:
            ev.ignore()
        else:
            #position = s.mapSceneToView(ev.pos())
            event_position = ev.pos()
            scene_pos = s.mapToScene(event_position)
            position = s.mapSceneToView(scene_pos)
            if s.click_callback != None:
                s.click_callback(position)
        ev.accept()





##############################################################################
##############################################################################


#class THzImage(pg.PlotWidget):
class THzImageObj(QHBoxLayout):
    image_data      = None
    update_cntr     = 0

    x_grid_1d      = None
    y_grid_1d      = None

    x_grid_2d      = None
    y_grid_2d      = None

    pixel_grid = None
    valid_pixels_grid = None
    
    # signal defintions
    new_pix_clicked = Signal(object, object, object)


    def __init__(s, thz_image_tab, cfg_dict, sing_pix_flag=False, 
                 main_image=False):
        super().__init__()

        # we're actually going to stack the plot widgets on top
        # of one another and make only one of them visible at a time
        s.thz_image_stack = QStackedWidget()
        s.main_image = main_image

        s.thz_image_tab   = thz_image_tab
        s.thz_mesh_obj    = THzMeshImage(thz_image_tab, sing_pix_flag, 
                                mouse_click_callback=s.mouse_click_event)
        s.thz_surface_obj = THzSurfaceObj(thz_image_tab)

        s.thz_image_stack.addWidget(s.thz_mesh_obj)
        s.thz_image_stack.addWidget(s.thz_surface_obj)
        s.thz_image_stack.setCurrentIndex(0)

        # color bar object
        s.color_bar_wg = pg.GraphicsLayoutWidget()
        s.color_bar_wg.setBackground(None)

        s.color_bar = pg.ColorBarItem(width=15, interactive=False)
        s.color_bar_wg.addItem(s.color_bar)

        # final layout
        s.addWidget(s.thz_image_stack, 100)
        s.addWidget(s.color_bar_wg, 10)

        s.cfg_dict = cfg_dict

        # initializing the dimensions of the image
        s.min_x = None
        s.max_x = None

        s.min_y = None
        s.max_y = None



    def set_mesh_opacity(s, opacity):
        s.thz_mesh_obj.set_mesh_opacity(opacity)


    def get_nearest_pix_ind(s, position):
        if (type(s.x_grid_1d) != type(None)) and (type(s.y_grid_1d) != type(None)):
            x_val = position.x()
            y_val = position.y()

            # need the size of a pixel in encoder counts
            pix_x_len = np.abs(s.x_grid_1d[1] - s.x_grid_1d[0])
            pix_y_len = np.abs(s.y_grid_1d[1] - s.y_grid_1d[0])

            # need to increase the x and y values by half a pixel
            x_val -= float(pix_x_len) / 2
            y_val -= float(pix_y_len) / 2

            # grab the nearest indices
            x_ind = np.argmin(np.abs(s.x_grid_1d - x_val))
            y_ind = np.argmin(np.abs(s.y_grid_1d - y_val))
            return (x_ind, y_ind)
        else:
            return (None, None)

    # handle mouse events for the single pixel tab
    def mouse_click_event(s, position):
        (x_ind, y_ind) = s.get_nearest_pix_ind(position)
        if x_ind != None:
            s.new_pix_clicked.emit(position, x_ind, y_ind)


    def calc_coarse_grids(s, new_xlen, new_ylen):
        """
        Only needs to be done if there's a change in the frame dimensions
        or number of x or y pixels.  Should be "infrequent"
        """
        min_x      = s.cfg_dict["min_x"]
        s.min_x    = min_x
        max_x      = s.cfg_dict["max_x"]
        s.max_x    = max_x

        min_y      = s.cfg_dict["min_y"]
        s.min_y    = min_y
        max_y      = s.cfg_dict["max_y"]
        s.max_y    = max_y

        xlen        = new_xlen
        s.xlen      = xlen
        ylen        = new_ylen
        s.ylen      = ylen

        s.x_grid_1d = np.linspace(min_x, max_x, xlen)
        s.y_grid_1d = np.linspace(min_y, max_y, ylen)

        # due to the strange way that the mesh grid plots we have to do this
        x_grid_1d_adj = np.append(s.x_grid_1d, s.x_grid_1d[-1])
        y_grid_1d_adj = np.append(s.y_grid_1d, s.y_grid_1d[-1])

        ylen_adj = ylen + 1
        xlen_adj = xlen + 1


        s.x_grid_2d = (np.tile(x_grid_1d_adj, ylen_adj).reshape((ylen_adj,
                        xlen_adj))).T
        s.y_grid_2d = np.tile(y_grid_1d_adj, xlen_adj).reshape((xlen_adj,
                        ylen_adj))

        # convert the grids to centimeters
        y_to_cm = s.cfg_dict["y_encoder_to_cm"]
        x_to_cm = s.cfg_dict["x_encoder_to_cm"]
        s.x_grid_1d_cm = s.x_grid_1d * x_to_cm
        s.y_grid_1d_cm = s.y_grid_1d * y_to_cm


    def check_frame_params(s, new_xlen, new_ylen):
        """
        Checks to see if any of the frame parameters that would require a 
        recalculation of the coarse grids have changed.  Returns true if the
        coarse grids need to be recalculated, returns false otherwise 
        """
        if s.min_x != s.cfg_dict["min_x"]:
            needs_update = True
        elif s.max_x != s.cfg_dict["max_x"]:
            needs_update = True
        elif s.min_y != s.cfg_dict["min_y"]:
            needs_update = True
        elif s.max_y != s.cfg_dict["max_y"]:
            needs_update = True
        elif s.xlen != new_xlen:
            needs_update = True
        elif s.ylen != new_ylen:
            needs_update = True
        else:
            needs_update = False
        return needs_update


    def update_image(s, frame_data, new_frame_flag, reset_camera=False, 
                     set_trace_val=False):
        """
        This performs the actual image updating.  Replaces update_plot()
        """

        cfg_dict = s.cfg_dict 

        if new_frame_flag:
            s.pixel_grid   = frame_data["pixel_grid"]
            s.valid_pixels_grid   = frame_data["valid_pixels_grid"]

            # first step is to check if the coarse grids need updating
            # we have to use the pixel_grid shape to infer xlen and
            # ylen because the cfg_dict values are "ahead" of the current
            # frame
            (new_xlen, new_ylen) = s.pixel_grid.shape
            if s.check_frame_params(new_xlen, new_ylen):
                s.calc_coarse_grids(new_xlen, new_ylen)
                print("recalculated grids")

            # construct a version with nans for ease of use
            s.pixel_grid_nans = copy.deepcopy(
                    frame_data["pixel_grid"])
                
            s.pixel_grid_nans[~s.valid_pixels_grid] = np.nan
        
        # only continue if there is a real frame stored in the class
        if type(s.pixel_grid) != type(None):
            # Now figure out the color scale limits
            autocolor = cfg_dict["autoscale_color"]
            cmap_str  = cfg_dict["colormap"]
            if not autocolor:
                color_min = cfg_dict["color_scale_min"]
                color_max = cfg_dict["color_scale_max"]
            else:
                flat_img = s.pixel_grid_nans.flatten()
                flat_img = np.sort(flat_img)
                flat_img = flat_img[~np.isnan(flat_img)]
                color_max = np.nanpercentile(flat_img, 90)
                color_min = np.nanpercentile(flat_img, 10)

                # set the color scale textboxes to the autoscaled values
                # when autoscale color is enabled

                if s.main_image:
                    s.thz_image_tab.update_autocolors(color_min, color_max)

            if (not math.isnan(color_min)) and (not math.isnan(color_max)):
                plot_style = cfg_dict["plot_style"]
                if plot_style in ["front_peak_range", "back_peak_range", 
                                  "integ_power_plot", "num_avgs_plot"]:
                    s.thz_image_stack.setCurrentIndex(0)
                    s.thz_mesh_obj.update_plot(s.x_grid_2d, s.y_grid_2d, 
                            s.pixel_grid, cmap_str, color_min, color_max, 
                            reset_camera, set_trace_val)
                                                  

                elif plot_style in ["front_surface_range", "back_surface_range"]:
                    s.thz_image_stack.setCurrentIndex(1)
                    s.thz_surface_obj.update_plot(s.x_grid_1d_cm, s.y_grid_1d_cm, 
                            s.pixel_grid_nans, cmap_str, 
                            color_min, color_max, reset_camera, set_trace_val)
                            

                else:
                    except_str = f"unsupported or invalid plot style: {plot_style}"
                    raise Exception(except_str)

                # I'll need to fix this to show the surface plot colormap
                cmap = pg.colormap.getFromMatplotlib(cmap_str) 
                s.color_bar.setColorMap(cmap)
                s.color_bar.setLevels((color_min, color_max))




    # NOTE CONSIDER PUSHING THIS LOGIC BACK INTO THzImageTab()
    def save_cur_image(s, fpath, desc):
        """
        saves the current image to file, will probably move this to the 
        seperate image types later so the appropriate image class will save
        the image
        """
        pixel_grid = s.pixel_grid

        cfg_dict = s.cfg_dict
        x_grid     = s.x_grid_1d
        y_grid     = s.y_grid_1d

        # Now figure out the color scale limits
        autocolor = s.cfg_dict["autoscale_color"]
        cmap_str  = s.cfg_dict["colormap"]
        if not autocolor:
            color_min = s.cfg_dict["color_scale_min"]
            color_max = s.cfg_dict["color_scale_max"]
        else:
            flat_img = s.pixel_grid_nans.flatten()
            color_min = np.nanmin(flat_img)
            color_max = np.nanmax(flat_img)

        plot_style = cfg_dict["plot_style"]
        cmap_str   = cfg_dict["colormap"]


        fig, ax = plt.subplots()
        plt.imshow(pixel_grid.T, extent=[x_grid.min(), x_grid.max(), 
                                        y_grid.min(), y_grid.max()],
                                        aspect='equal', origin='lower', 
                                        cmap=cmap_str, vmin=color_min, 
                                        vmax=color_max)
        plt.gca().invert_xaxis()  # Reverse x-axis
        plt.gca().invert_yaxis()  # Reverse y-axis

        if plot_style in ["front_peak_range"]:
            plt.colorbar(label='range [cm]')
            plt.title('front peak range, initial\n' + desc)

        elif plot_style in ["back_peak_range"]:
            plt.colorbar(label='range [cm]')
            plt.title('back peak range, initial\n' + desc)

        elif plot_style in ["integ_power_plot"]:
            plt.colorbar(label='power [dB]')
            plt.title('integrated power plot\n' + desc)

        elif plot_style in ["num_avgs_plot"]:
            plt.colorbar(label='num avgs')
            plt.title('number of averages plot\n' + desc)

        else:
            plt.colorbar(label='?')
            plt.title('unknown plot type\n' + desc)

        plt.xlabel('X')
        plt.ylabel('Y')
        fig.set_figheight(6)
        fig.tight_layout()
        print(f"fpath = {fpath}")
        fig.savefig(fpath)

        plt.close(fig)
        #if plot_style in ["front_peak_range", "back_peak_range", 
        #"integ_power_plot", "num_avgs_plot"]:


##############################################################################
##############################################################################
##############################################################################
##############################################################################


class THzMeshImage(pg.PlotWidget):
    """
    This is the 

    """
    thz_image_tab   = None
    
    def __init__(s, thz_image_tab, sing_pix_flag=False, 
                    mouse_click_callback=None):
        if sing_pix_flag:
            s.view_box = MyViewBox(click_callback=mouse_click_callback)
            plot_item = pg.PlotItem(viewBox=s.view_box)
            super().__init__(viewBox=s.view_box)
        else:
            super().__init__()
        s.sing_pix_flag = sing_pix_flag

        s.thz_image_tab = thz_image_tab

        # Removes warning spammed in console (also might disable touch 
        # screen but i dont think we're using that)
        s.viewport().setAttribute(
            QtCore.Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

        # main color mesh image
        s.color_mesh = pg.PColorMeshItem()
        s.color_mesh.setColorMap(pg.colormap.getFromMatplotlib("jet_r"))
        s.plot_item = s.getPlotItem()
        s.addItem(s.color_mesh)


        s.setTitle("THz Image")
        s.plot_item.invertX(False)
        s.plot_item.invertY(False)
        s.plot_item.setAspectLocked(True)


    def set_levels(s, min_val, max_val):
        s.color_mesh.setLevels((min_val, max_val))

    def set_mesh_opacity(s, opacity):
        s.color_mesh.setOpacity(opacity)


    def update_plot(s, x_grid_2d, y_grid_2d, image, cmap_str, color_min, 
                    color_max, reset_camera=False, set_trace_val=False):
        s.set_levels(color_min, color_max)

        s.color_mesh.setData(x_grid_2d, y_grid_2d, image, autoLevels=False)
        cmap = pg.colormap.getFromMatplotlib(cmap_str) 
        s.color_mesh.setColorMap(cmap)


##############################################################################
##############################################################################
##############################################################################
##############################################################################

# NOTE A LOT OF WORK TO DO ON THIS 
class THzSurfaceObj(gl.GLViewWidget):
    """
    This is a widget that contains a surface plot for the THz data
    """
    first_update    = True

    # only gets sort of close to the colormap, not exactly 
    cmap_dict = None


    def __init__(s, thz_image_tab):
        super().__init__(rotationMethod="quaternion")

        s.thz_image_tab = thz_image_tab

        s.surface_plot = gl.GLSurfacePlotItem()
        s.addItem(s.surface_plot)
        distance    = 1.0
        elevation   = -72.0
        azimuth     = 442.0
        fov         = 127
        pos = pg.Vector(-3.3, 19.9, 380) 
        s.setCameraParams(center=pos, distance=distance, fov=fov, 
                             elevation=elevation, azimuth=azimuth)

        # NOTE This needs to be upgraded
        # organization is: [min_rgb, max_rgb]
        s.cmap_dict = {}
        s.cmap_dict["jet"]        = [(0.,0.,1.),(1.,0.,0.)]
        s.cmap_dict["jet_r"]      = [(1.,0.,0.),(0.,0.,1.)]
        s.cmap_dict["gray"]       = [(0.,0.,0.),(1.,1.,1.)]
        s.cmap_dict["binary"]     = [(1.,1.,1.),(0.,0.,0.)]
        s.cmap_dict["Blues"]      = [(1.,1.,1.),(0.,0.,1.)]
        s.cmap_dict["Greens"]     = [(1.,1.,1.),(0.,1.,0.)]
        s.cmap_dict["Reds"]       = [(1.,1.,1.),(1.,0.,0.)]
        s.cmap_dict["copper"]     = [(0.05,0.05,0.05),(0.722,0.451,0.2)]
        s.cmap_dict["twilight"]   = [(0.8,0.8,0.8),(0.125, 0.,0.125)]


    def set_levels(s, min_val, max_val):
        s.surface_plot.setLevels((min_val, max_val))


    def update_plot(s, x_grid_cm, y_grid_cm, image, cmap_str, color_min, 
                    color_max, reset_camera=False, set_trace_val=False):

        image_adj = image
        image_adj = np.flip(image, 1)

        # color_min and color_max are acutally the range values for min and 
        # max color, 
        if cmap_str in s.cmap_dict:
            [cmap_min, cmap_max] = s.cmap_dict[cmap_str]
        else:
            cmap = matplotlib.colormaps.get_cmap(cmap_str)
            cmap_min = cmap(0.0)[:3]
            cmap_max = cmap(1.0)[:3]
        s.color_map = s.rgb_colormap(cmap_min, cmap_max, color_min, color_max)

        color_map = s.color_map

        s.surface_plot.setData(x_grid_cm, y_grid_cm, image_adj)
        s.surface_plot.setShader("heightColor")
        s.surface_plot.shader()["colorMap"] = color_map

        if (s.first_update) or (reset_camera):
            s.first_update = False
            distance    = 40.0
            fov         = 25
            rotation    = QtGui.QQuaternion(0.0, 0.0, -1.0, 0.0)
            pos_x = 0.0
            pos_y = (np.nanmax(y_grid_cm) - np.nanmin(y_grid_cm)) / 2
            pos_z = color_min
            pos         = pg.Vector(pos_x, pos_y, pos_z) 
            s.setCameraParams(center=pos, distance=distance, fov=fov, 
                                 rotation=rotation)


    ###########################################################################
    ###################### Surface Plot Colormap Related ######################
    ###########################################################################

    def rgb_colormap(s, min_color, max_color, min_val, max_val):
        """
        this generates a colormap that smoothly goes from min_color to 
        max_color.  min_color and max_color are a tuple of three RGB floats
        that vary from 0 to 1.

        """
        span = max_val - min_val

        (rk0, rk1) = s.conv_rgb(min_color[0], max_color[0], min_val, max_val)
        (gk0, gk1) = s.conv_rgb(min_color[1], max_color[1], min_val, max_val)
        (bk0, bk1) = s.conv_rgb(min_color[2], max_color[2], min_val, max_val)

        red_vals    = [rk0, rk1, 1]
        green_vals  = [gk0, gk1, 1]
        blue_vals   = [bk0, bk1, 1]
        colormap    = red_vals + green_vals + blue_vals
        #print(f"colormap = {colormap}")
        return colormap


    def conv_rgb(s, min_single_color, max_single_color, min_val, max_val):
        """
        converts an rgb color tuple to the constants required for generating 
        a colormap
        """

        if abs(min_single_color - max_single_color) < 0.01:
            #k1 = 2e6
            k1 = 1e6
            k0 = 1./1e6

        else:
            #min_single_color = 2.0 * min_single_color
            #max_single_color = 2.0 * max_single_color

            k1  = ((max_single_color*min_val - min_single_color*max_val) 
                   / (min_single_color - max_single_color))

            if abs(min_val + k1) > 0.01:
                k0 = min_single_color / (min_val + k1)
            elif abs(max_val + k1) > 0.01:
                k0 = max_single_color / (max_val + k1)
            else:
                raise ValueError(f"conv_rgb: degenerate color mapping for "
                                 f"min_val={min_val}, max_val={max_val}")

        return (k0, k1)





