"""
This module defines the majority of geoplot functions, including all plot types.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import warnings
from geoplot.quad import QuadTree
import shapely.geometry
import pandas as pd
import descartes

try:
    from geopandas.plotting import _mapclassify_choro
except ImportError:
    from geopandas.plotting import __pysal_choro as _mapclassify_choro

__version__ = "0.2.4"


def pointplot(
    df, projection=None,
    hue=None, scheme=None, k=5, cmap='viridis',
    scale=None, limits=(0.5, 2), scale_func=None,
    legend=False, legend_var=None, legend_values=None, legend_labels=None, legend_kwargs=None,
    figsize=(8, 6), extent=None, ax=None, **kwargs
):
    """
    A scatter plot, where data value(s) are represented as a coordinate point on a map.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        The projection to use. For reference see
        `Working with Projections <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Working%20with%20Projections.ipynb>`_.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The column in the dataset (or an iterable of some other data) used to color the points.
        For reference see
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Hue>`_.
    scheme : None or {"quantiles"|"equal_interval"|"fisher_jenks"}, optional
        If ``hue`` is specified, the map classifier to use.
    k : int or None, optional
        If ``hue`` is specified, the number of colors to use.
    cmap : matplotlib color, optional
        If ``hue`` is specified, the
        `matplotlib colormap <http://matplotlib.org/examples/color/colormaps_reference.html>`_ to use.
    scale : str or iterable, optional
        The column in the dataset (or an iterable of some other data) with which to scale output
        points. For reference see
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Scale>`_.
    limits : (min, max) tuple, optional
        The minimum and maximum scale limits.
    scale_func : ufunc, optional
        The function used to scale point sizes.
    legend : boolean, optional
        Whether to include a legend.
    legend_values : list, optional
        The values to use in the legend. Defaults to equal intervals. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_labels : list, optional
        The names to use in the legend. Defaults to the variable values. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_var : "hue" or "scale", optional
        Which variable (``hue`` or ``scale``) to use in the legend.
    legend_kwargs : dict, optional
        Keyword arguments to be passed to 
        `the underlying legend <http://matplotlib.org/users/legend_guide.html>`_.
    extent : None or (min_longitude, max_longitude, min_latitude, max_latitude), optional
        Controls the plot extents. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the
        resultant plot.
    ax : AxesSubplot or GeoAxesSubplot instance, optional
        A ``matplotlib.axes.AxesSubplot`` or ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance.
        Defaults to a new axis.
    kwargs: dict, optional
        Keyword arguments to be passed to the underlying `scatter plot
        <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    Returns
    -------
    ``AxesSubplot`` or ``GeoAxesSubplot``
        The plot axis

    Examples
    --------

    The ``pointplot`` is a `geospatial scatter plot 
    <https://en.wikipedia.org/wiki/Scatter_plot>`_ that represents each observation in your dataset
    with a single point. It is simple and easily interpretable plot that is nearly universally
    understood, making it an ideal choice for showing simple pointwise relationships between
    observations.

    ``df`` should be a ``GeoDataFrame`` of ``shapely.geometry.Point`` geometries:

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as gcrs
        gplt.pointplot(points)

    .. image:: ../figures/pointplot/pointplot-initial.png


    The ``hue`` parameter accepts a data column and applies a colormap to the output. The
    ``legend`` parameter toggles a legend.

    .. code-block:: python

        gplt.pointplot(cities, projection=gcrs.AlbersEqualArea(), hue='ELEV_IN_FT', legend=True)

    .. image:: ../figures/pointplot/pointplot-legend.png

    The ``pointplot`` binning methodology is controlled using by `scheme`` parameter. The default
    is ``quantile``, which bins observations into classes of different sizes but the same numbers
    of observations. ``equal_interval`` will creates bins that are the same size, but potentially
    containing different numbers of observations. The more complicated ``fisher_jenks`` scheme is
    an intermediate between the two.

    .. code-block:: python

        gplt.pointplot(cities, projection=gcrs.AlbersEqualArea(), hue='ELEV_IN_FT',
                       legend=True, scheme='equal_interval')

    .. image:: ../figures/pointplot/pointplot-scheme.png

    Alternatively, your data may already be `categorical
    <http://pandas.pydata.org/pandas-docs/stable/categorical.html>`_. ``geoplot`` will account for
    this automatically:

    .. code-block:: python

        gplt.pointplot(collisions, projection=gcrs.AlbersEqualArea(), hue='BOROUGH',
                       legend=True)

    .. image:: ../figures/pointplot/pointplot-categorical.png

    Keyword arguments can be passed to the legend using the ``legend_kwargs`` argument. These
    arguments will be passed to the underlying ``matplotlib.legend.Legend`` instance (`ref
    <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_). The ``loc`` and
    ``bbox_to_anchor`` parameters are particularly useful for positioning the legend. Other
    additional arguments will be passed to the underlying ``matplotlib``
    `scatter plot <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    .. code-block:: python

        gplt.pointplot(collisions[collisions['BOROUGH'].notnull()], 
                       projection=gcrs.AlbersEqualArea(),
                       hue='BOROUGH',
                       legend=True, legend_kwargs={'loc': 'upper left'},
                       edgecolor='white', linewidth=0.5)

    .. image:: ../figures/pointplot/pointplot-kwargs.png

    Change the number of bins by specifying an alternative ``k`` value. Adjust the `colormap
    <http://matplotlib.org/examples/color/colormaps_reference.html>`_ using the ``cmap`` parameter.
    To use a continuous colormap, explicitly specify ``k=None``. Note that if ``legend=True``, a
    ``matplotlib`` `colorbar legend <http://matplotlib.org/api/colorbar_api.html>`_ will be used.

    .. code-block:: python

        gplt.pointplot(data, projection=gcrs.AlbersEqualArea(),
                       hue='var', k=8,
                       edgecolor='white', linewidth=0.5,
                       legend=True, legend_kwargs={'bbox_to_anchor': (1.25, 1.0)})

    .. image:: ../figures/pointplot/pointplot-k.png

    ``scale`` provides an alternative or additional visual variable.

    .. code-block:: python

        gplt.pointplot(collisions, projection=gcrs.AlbersEqualArea(),
                       scale='NUMBER OF PERSONS INJURED',
                       legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/pointplot/pointplot-scale.png

    The limits can be adjusted to fit your data using the ``limits`` parameter.

    .. code-block:: python

        gplt.pointplot(collisions, projection=gcrs.AlbersEqualArea(),
                       scale='NUMBER OF PERSONS INJURED', limits=(0, 10),
                       legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/pointplot/pointplot-limits.png

    The default scaling function is linear: an observations at the midpoint of two others will be
    exactly midway between them in size. To specify an alternative scaling function, use the
    ``scale_func`` parameter. This should be a factory function of two variables which, when given
    the maximum and minimum of the dataset, returns a scaling function which will be applied to
    the rest of the data. A demo is available in the
    `example gallery <examples/usa-city-elevations.html>`_.

    .. code-block:: python

        def trivial_scale(minval, maxval):
            def scalar(val):
                return 2
            return scalar

        gplt.pointplot(collisions, projection=gcrs.AlbersEqualArea(),
                       scale='NUMBER OF PERSONS INJURED', scale_func=trivial_scale,
                       legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/pointplot/pointplot-scale-func.png

    ``hue`` and ``scale`` can co-exist. In case more than one visual variable is used, control
    which one appears in the legend using ``legend_var``.

    .. code-block:: python

        gplt.pointplot(collisions[collisions['BOROUGH'].notnull()],
                       projection=gcrs.AlbersEqualArea(),
                       hue='BOROUGH',
                       scale='NUMBER OF PERSONS INJURED', limits=(0, 10),
                       legend=True, legend_kwargs={'loc': 'upper left'},
                       legend_var='scale')

    .. image:: ../figures/pointplot/pointplot-legend-var.png

    """
    # Initialize the figure, if one hasn't been initialized already.
    _init_figure(ax, figsize)

    xs = np.array([p.x for p in df.geometry])
    ys = np.array([p.y for p in df.geometry])

    if projection:
        # Properly set up the projection.
        projection = projection.load(df, {
            'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
            'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
        })

        # Set up the axis.
        if not ax:
            ax = plt.subplot(111, projection=projection)

        # Set extent.
        if extent:
            ax.set_extent(extent)
        else:
            pass  # Default extent.
    else:
        if not ax:
            ax = plt.gca()

    # Clean up patches.
    _lay_out_axes(ax, projection)

    # Immediately return if input geometry is empty.
    if len(df.geometry) == 0:
        return ax

    # Parse hue and scale inputs.
    hue = _to_geoseries(df, hue)
    scalar_values = _to_geoseries(df, scale)

    # Set legend variable.
    legend_var = _set_legend_var(legend_var, hue, scale)

    # Generate the coloring information, if needed. Follows one of two schemes, 
    # categorical or continuous, based on whether or not ``k`` is specified (``hue`` must be
    # specified for either to work).
    if k is not None:
        # Categorical colormap code path.
        categorical, scheme = _validate_buckets(hue, scheme)

        if hue is not None:
            cmap, categories, hue_values = _discrete_colorize(
                categorical, hue, scheme, k, cmap
            )
            colors = [cmap.to_rgba(v) for v in hue_values]

            # Add a legend, if appropriate.
            if legend and (legend_var != "scale" or scale is None):
                _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs)
        else:
            if 'color' not in kwargs.keys():
                colors = ['steelblue']*len(df)
            else:
                colors = [kwargs['color']]*len(df)
                kwargs.pop('color')
    elif k is None and hue is not None:
        # Continuous colormap code path.
        hue_values = hue
        cmap = _continuous_colormap(hue_values, cmap)
        colors = [cmap.to_rgba(v) for v in hue_values]

        # Add a legend, if appropriate.
        if legend and (legend_var != "scale" or scale is None):
            _paint_colorbar_legend(ax, hue_values, cmap, legend_kwargs)

    # Check if the ``scale`` parameter is filled, and use it to fill a ``values`` name.
    if scale is not None:
        # Compute a scale function.
        dmin, dmax = np.min(scalar_values), np.max(scalar_values)
        if not scale_func:
            dslope = (limits[1] - limits[0]) / (dmax - dmin)
            # edge case: if dmax, dmin are <=10**-30 or so, will overflow and eval to infinity.
            # TODO: better explain this error
            if np.isinf(dslope): 
                raise ValueError(
                    "The data range provided to the 'scale' variable is too small for the default "
                    "scaling function. Normalize your data or provide a custom 'scale_func'."
                )
            dscale = lambda dval: limits[0] + dslope * (dval - dmin)
        else:
            dscale = scale_func(dmin, dmax)

        # Apply the scale function.
        scalar_multiples = np.array([dscale(d) for d in scalar_values])
        sizes = scalar_multiples * 20

        # When a scale is applied, large points will tend to obfuscate small ones. Bringing the
        # smaller points to the front (by plotting them last) is a necessary intermediate step,
        # which is what this bit of code does.
        sorted_indices = np.array(
            sorted(enumerate(sizes), key=lambda tup: tup[1])[::-1]
        )[:,0].astype(int)
        xs = np.array(xs)[sorted_indices]
        ys = np.array(ys)[sorted_indices]
        sizes = np.array(sizes)[sorted_indices]
        colors = np.array(colors)[sorted_indices]

        # Draw a legend, if appropriate.
        if legend and (legend_var == "scale" or hue is None):
            _paint_carto_legend(
                ax, scalar_values, legend_values, legend_labels, dscale, legend_kwargs
            )
    else:
        sizes = kwargs.pop('s') if 's' in kwargs.keys() else 20

    # Draw.
    if projection:
        ax.scatter(xs, ys, transform=ccrs.PlateCarree(), c=colors, s=sizes, **kwargs)
    else:
        ax.scatter(xs, ys, c=colors, s=sizes, **kwargs)

    return ax


def polyplot(
    df, projection=None,
    extent=None, figsize=(8, 6), edgecolor='black', facecolor='None', ax=None, **kwargs
):
    """
    Polygons on a map.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        The projection to use. For reference see
        `Working with Projections <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Working%20with%20Projections.ipynb>`_.
    extent : None or (min_longitude, max_longitude, min_latitude, max_latitude), optional
        Controls the plot extents. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the
        resultant plot. Defaults to (8, 6), the ``matplotlib`` default global.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the
        resultant plot.
    ax : AxesSubplot or GeoAxesSubplot instance, optional
        A ``matplotlib.axes.AxesSubplot`` or ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance.
        Defaults to a new axis.
    kwargs: dict, optional
        Keyword arguments to be passed to the underlying ``matplotlib`` `Polygon patches
        <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_.

    Returns
    -------
    ``AxesSubplot`` or ``GeoAxesSubplot``
        The plot axis

    Examples
    --------

    The polyplot can be used to draw simple, unembellished polygons. A trivial example can be
    created with just a geometry and, optionally, a projection.

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as gcrs
        gplt.polyplot(boroughs, projection=gcrs.AlbersEqualArea())


    .. image:: ../figures/polyplot/polyplot-initial.png

    However, note that ``polyplot`` is mainly intended to be used in concert with other plot types.

    .. code-block:: python

        ax = gplt.polyplot(boroughs, projection=gcrs.AlbersEqualArea())
        gplt.pointplot(collisions[collisions['BOROUGH'].notnull()], 
                       projection=gcrs.AlbersEqualArea(),
                       hue='BOROUGH',
                       legend=True, edgecolor='white', linewidth=0.5,
                       legend_kwargs={'loc': 'upper left'},
                       ax=ax)


    .. image:: ../figures/polyplot/polyplot-stacked.png

    Additional keyword arguments are passed to the underlying ``matplotlib`` `Polygon patches
    <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_.

    .. code-block:: python

        ax = gplt.polyplot(boroughs, projection=gcrs.AlbersEqualArea(),
                           linewidth=0, facecolor='lightgray')


    .. image:: ../figures/polyplot/polyplot-kwargs.png
    """
    # Initialize the figure.
    _init_figure(ax, figsize)

    if projection:
        # Properly set up the projection.
        projection = projection.load(df, {
            'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
            'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
        })

        # Set up the axis.
        if not ax:
            ax = plt.subplot(111, projection=projection)

    else:
        if not ax:
            ax = plt.gca()

    # Clean up patches.
    _lay_out_axes(ax, projection)

    # Immediately return if input geometry is empty.
    if len(df.geometry) == 0:
        return ax

    # Set extent.
    extrema = _get_envelopes_min_maxes(df.geometry.envelope.exterior)
    _set_extent(ax, projection, extent, extrema)

    # Finally we draw the features.
    if projection:
        for geom in df.geometry:
            features = ShapelyFeature([geom], ccrs.PlateCarree())
            ax.add_feature(features, facecolor=facecolor, edgecolor=edgecolor, **kwargs)
    else:
        for geom in df.geometry:
            try:  # Duck test for MultiPolygon.
                for subgeom in geom:
                    feature = descartes.PolygonPatch(
                        subgeom, facecolor=facecolor, edgecolor=edgecolor, **kwargs
                    )
                    ax.add_patch(feature)
            except (TypeError, AssertionError):  # Shapely Polygon.
                feature = descartes.PolygonPatch(
                    geom, facecolor=facecolor, edgecolor=edgecolor, **kwargs
                )
                ax.add_patch(feature)

    return ax


def choropleth(
    df, projection=None,
    hue=None, scheme=None, k=5, cmap='viridis',
    legend=False, legend_kwargs=None, legend_labels=None,
    extent=None, figsize=(8, 6), ax=None, **kwargs
):
    """
    A well-known area plot.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        The projection to use. For reference see
        `Working with Projections <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Working%20with%20Projections.ipynb>`_.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The column in the dataset (or an iterable of some other data) used to color the points.
        For reference see
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Hue>`_.
    scheme : None or {"quantiles"|"equal_interval"|"fisher_jenks"}, optional
        If ``hue`` is specified, the map classifier to use.
    k : int or None, optional
        Ignored if ``hue`` is left unspecified. Otherwise, if ``categorical`` is False, controls
        how many colors to use (5 is the default). If set to ``None``, a continuous colormap will
        be used.
    cmap : matplotlib color, optional
        If ``hue`` is specified, the
        `matplotlib colormap <http://matplotlib.org/examples/color/colormaps_reference.html>`_ to use.
    legend : boolean, optional
        Whether or not to include a legend. Ignored if neither a ``hue`` nor a ``scale`` is
        specified.
    legend_values : list, optional
        The values to use in the legend. Defaults to equal intervals. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_labels : list, optional
        The names to use in the legend. Defaults to the variable values. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_kwargs : dict, optional
        Keyword arguments to be passed to 
        `the underlying legend <http://matplotlib.org/users/legend_guide.html>`_.
    extent : None or (min_longitude, max_longitude, min_latitude, max_latitude), optional
        Controls the plot extents. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the
        resultant plot.
    ax : AxesSubplot or GeoAxesSubplot instance, optional
        A ``matplotlib.axes.AxesSubplot`` or ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance.
        Defaults to a new axis.
    kwargs: dict, optional
        Keyword arguments to be passed to the underlying ``matplotlib`` `Polygon patches
        <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_.

    Returns
    -------
    ``AxesSubplot`` or ``GeoAxesSubplot``
        The plot axis

    Examples
    --------

    A choropleth takes observations that have been aggregated on some meaningful polygonal level
    (e.g. census tract, state, country, or continent) and displays the data to the reader using
    color. It is a well-known plot type, and likeliest the most general-purpose and well-known of
    the specifically spatial plot types. It is especially powerful when combined with meaningful
    or actionable aggregation areas; if no such aggregations exist, or the aggregations you have
    access to are mostly incidental, its value is more limited.

    The ``choropleth`` requires a series of enclosed areas consisting of ``shapely`` ``Polygon``
    or ``MultiPolygon`` entities, and a set of data about them that you would like to express in
    color. A basic choropleth requires geometry, a ``hue`` variable, and, optionally, a projection.

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as gcrs
        gplt.choropleth(polydata, hue='latdep', projection=gcrs.PlateCarree())

    .. image:: ../figures/choropleth/choropleth-initial.png

    Change the colormap with the ``cmap`` parameter.

    .. code-block:: python

        gplt.choropleth(polydata, hue='latdep', projection=gcrs.PlateCarree(), cmap='Blues')

    .. image:: ../figures/choropleth/choropleth-cmap.png

    ``geoplot`` will automatically do the right thing if your variable is `categorical
    <http://pandas.pydata.org/pandas-docs/stable/categorical.html>`_ instead. To add a legend,
    specify a ``legend``.

    .. code-block:: python

        gplt.choropleth(boroughs, projection=gcrs.AlbersEqualArea(), hue='BoroName',
                        legend=True)

    .. image:: ../figures/choropleth/choropleth-legend.png

    Keyword arguments can be passed to the legend using the ``legend_kwargs`` argument. These
    arguments will be passed to the underlying ``matplotlib.legend.Legend`` instance (`ref
    <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_). The ``loc`` and
    ``bbox_to_anchor`` parameters are particularly useful for positioning the legend. Other
    additional arguments will be passed to the underlying ``matplotlib``
    `scatter plot <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    .. code-block:: python

        gplt.choropleth(boroughs, projection=gcrs.AlbersEqualArea(), hue='BoroName',
                        legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/choropleth/choropleth-legend-kwargs.png

    Additional arguments not in the method signature will be passed as keyword parameters to the
    underlying 
    `matplotlib Polygon patches <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_.

    .. code-block:: python

        gplt.choropleth(boroughs, projection=gcrs.AlbersEqualArea(), hue='BoroName', 
                        linewidth=0)

    .. image:: ../figures/choropleth/choropleth-kwargs.png

    Choropleths default to splitting the data into five buckets with approximately equal numbers
    of observations in them. Change the number of buckets by specifying ``k``. Or, to use a
    continuous colormap, specify ``k=None``. In this case a colorbar legend will be used.

    .. code-block:: python

        gplt.choropleth(polydata, hue='latdep', cmap='Blues', k=None, legend=True,
                        projection=gcrs.PlateCarree())

    .. image:: ../figures/choropleth/choropleth-k-none.png

    The ``choropleth`` binning methodology is controlled using by `scheme`` parameter. The default
    is ``quantile``, which bins observations into classes of different sizes but the same numbers
    of observations. ``equal_interval`` will creates bins that are the same size, but potentially
    containing different numbers of observations. The more complicated ``fisher_jenks`` scheme is
    an intermediate between the two.

    .. code-block:: python

        gplt.choropleth(census_tracts, hue='mock_data', projection=gcrs.AlbersEqualArea(),
                legend=True, edgecolor='white', linewidth=0.5, legend_kwargs={'loc': 'upper left'},
                scheme='equal_interval')

    .. image:: ../figures/choropleth/choropleth-scheme.png
    """
    # Initialize the figure.
    _init_figure(ax, figsize)

    if projection:
        projection = projection.load(df, {
            'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
            'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
        })

        # Set up the axis.
        if not ax:
            ax = plt.subplot(111, projection=projection)
    else:
        if not ax:
            ax = plt.gca()

    # Clean up patches.
    _lay_out_axes(ax, projection)

    # Immediately return if input geometry is empty.
    if len(df.geometry) == 0:
        return ax

    # Set extent.
    extrema = _get_envelopes_min_maxes(df.geometry.envelope.exterior)
    _set_extent(ax, projection, extent, extrema)

    # Format the data to be displayed for input.
    hue = _to_geoseries(df, hue)
    if hue is None:
        raise ValueError("No 'hue' specified.")

    # Generate the coloring information, if needed. Follows one of two schemes, categorical or 
    # continuous, based on whether or not ``k`` is specified (``hue`` must be specified for either
    # to work).
    if k is not None:
        # Categorical colormap code path.

        # Validate buckets.
        categorical, scheme = _validate_buckets(hue, scheme)

        if hue is not None:
            cmap, categories, hue_values = _discrete_colorize(
                categorical, hue, scheme, k, cmap
            )
            colors = [cmap.to_rgba(v) for v in hue_values]

            # Add a legend, if appropriate.
            if legend:
                _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs)
        else:
            colors = ['steelblue']*len(df)
    elif k is None and hue is not None:
        # Continuous colormap code path.
        hue_values = hue
        cmap = _continuous_colormap(hue_values, cmap)
        colors = [cmap.to_rgba(v) for v in hue_values]

        # Add a legend, if appropriate.
        if legend:
            _paint_colorbar_legend(ax, hue_values, cmap, legend_kwargs)

    # Draw the features.
    if projection:
        for color, geom in zip(colors, df.geometry):
            features = ShapelyFeature([geom], ccrs.PlateCarree())
            ax.add_feature(features, facecolor=color, **kwargs)
    else:
        for color, geom in zip(colors, df.geometry):
            try:  # Duck test for MultiPolygon.
                for subgeom in geom:
                    feature = descartes.PolygonPatch(subgeom, facecolor=color, **kwargs)
                    ax.add_patch(feature)
            except (TypeError, AssertionError):  # Shapely Polygon.
                feature = descartes.PolygonPatch(geom, facecolor=color, **kwargs)
                ax.add_patch(feature)

    return ax


def quadtree(
    df, projection=None,
    hue=None, nmax=None, nmin=None, nsig=0, agg=np.mean,
    cmap='viridis', legend=True, legend_kwargs=None,
    extent=None, figsize=(8, 6), ax=None, **kwargs
):
    """
    Self-aggregating quadtree plot.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        The projection to use. For reference see
        `Working with Projections <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Working%20with%20Projections.ipynb>`_.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The column in the dataset (or an iterable of some other data) used to color the points.
        For reference see
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Hue>`_.
    cmap : matplotlib color, optional
        If ``hue`` is specified, the
        `matplotlib colormap <http://matplotlib.org/examples/color/colormaps_reference.html>`_ to use.
    nmax : int or None, optional
        The maximum number of observations in a quadrangle.
    nmin : int, optional
        The minimum number of observations in a quadrangle.
    nsig : int, optional
        The minimum number of observations in a quadrangle. Defaults to 0 (only empty patches are
        removed).
    agg : function, optional
        The aggregation func used for the colormap. Defaults to ``np.mean``.
    legend : boolean, optional
        Whether or not to include a legend.
    legend_values : list, optional
        The values to use in the legend. Defaults to equal intervals. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_labels : list, optional
        The names to use in the legend. Defaults to the variable values. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_kwargs : dict, optional
        Keyword arguments to be passed to 
        `the underlying legend <http://matplotlib.org/users/legend_guide.html>`_.
    extent : None or (min_longitude, max_longitude, min_latitude, max_latitude), optional
        Controls the plot extents. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the
        resultant plot.
    ax : AxesSubplot or GeoAxesSubplot instance, optional
        A ``matplotlib.axes.AxesSubplot`` or ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance.
        Defaults to a new axis.
    kwargs: dict, optional
        Keyword arguments to be passed to the underlying ``matplotlib`` `Polygon patches
        <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_.

    Returns
    -------
    ``AxesSubplot`` or ``GeoAxesSubplot``
        The plot axis

    Examples
    --------
    A quadtree is a tree data structure which splits a space into increasingly small rectangular
    fractals. This plot takes a sequence of point or polygonal geometries as input and builds a
    choropleth out of their centroids, where each region is a fractal quadrangle with at least
    ``nsig`` observations.

    A quadtree can replace a more conventional choropleth in certain cases where you lack region
    information and have a relatively homogeneous point distribution. A sufficiently large number
    of points `can construct a very detailed view of a space <https://i.imgur.com/n2xlycT.png>`_.

    A simple ``quadtree`` can be generated with a dataset, a data column of interest, and
    (optionally) a projection.

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as gcrs
        gplt.aggplot(collisions, projection=gcrs.PlateCarree(), hue='LATDEP')

    .. image:: ../figures/aggplot/aggplot-initial.png

    To get the best output, you often need to tweak the ``nmin`` and ``nmax`` parameters,
    controlling the minimum and maximum number of observations per box, respectively, yourself. In
    this case we'll also choose a different 
    `matplotlib colormap <http://matplotlib.org/examples/color/colormaps_reference.html>`_, using
    the ``cmap`` parameter.

    ``aggplot`` will satisfy the ``nmax`` parameter before trying to satisfy ``nmin``, so you may
    result in spaces without observations, or ones lacking a statistically significant number of
    observations. You can control the maximum number of observations in the blank spaces using the
    ``nsig`` parameter.

    .. code-block:: python

        gplt.aggplot(
            collisions, nmin=20, nmax=500, nsig=5, projection=gcrs.PlateCarree(),
            hue='LATDEP', cmap='Reds'
        )

    .. image:: ../figures/aggplot/aggplot-quadtree-tuned.png

    You'll have to play around with these parameters to get the clearest picture.

    Observations will be aggregated by average, by default. Specify an alternative aggregation
    using the ``agg`` parameter.

    ``legend`` toggles the legend. Additional keyword arguments for styling the `colorbar
    <http://matplotlib.org/api/colorbar_api.html>`_ legend are passed using ``legend_kwargs``.
    Other additional keyword arguments are passed to the underlying ``matplotlib`` `Polygon
    <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_ instances.
    """
    _init_figure(ax, figsize)

    # Set up projection.
    if projection:
        projection = projection.load(df, {
            'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
            'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
        })

        if not ax:
            ax = plt.subplot(111, projection=projection)
    else:
        if not ax:
            ax = plt.gca()

    # Clean up patches.
    _lay_out_axes(ax, projection)

    # Immediately return if input geometry is empty.
    if len(df.geometry) == 0:
        return ax

    # Up-convert input to a GeoDataFrame (necessary for quadtree comprehension).
    df = gpd.GeoDataFrame(df, geometry=df.geometry)

    # Type-constrain hue.
    if not isinstance(hue, str):
        hue_col = hash(str(hue))
        df[hue_col] = _to_geoseries(df, hue)
    else:
        hue_col = hue

    # Set reasonable defaults for the n-params if appropriate.
    nmax = nmax if nmax else len(df)
    nmin = nmin if nmin else np.max([1, np.min([20, int(0.05 * len(df))])])

    # Generate a quadtree.
    quad = QuadTree(df)
    bxmin, bxmax, bymin, bymax = quad.bounds

    # Assert that nmin is not smaller than the largest number of co-located observations
    # (otherwise the algorithm would continue running until the recursion limit).
    max_coloc = np.max([len(l) for l in quad.agg.values()])
    if max_coloc > nmin:
        raise ValueError(
            "nmin is set to {0}, but there is a coordinate containing {1} observations in the "
            "dataset.".format(nmin, max_coloc)
        )

    # Run the partitions.
    partitions = list(quad.partition(nmin, nmax))

    # Generate colormap.
    values = [agg(p.data[hue_col]) for p in partitions if p.n > nsig]
    cmap = _continuous_colormap(values, cmap)

    for p in partitions:
        xmin, xmax, ymin, ymax = p.bounds
        rect = shapely.geometry.Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])
        color = cmap.to_rgba(agg(p.data[hue_col])) if p.n > nsig else "white"
        if projection:
            feature = ShapelyFeature([rect], ccrs.PlateCarree())
            ax.add_feature(feature, facecolor=color, **kwargs)
        else:
            feature = descartes.PolygonPatch(rect, facecolor=color, **kwargs)
            ax.add_patch(feature)

    # Set extent.
    extrema = (bxmin, bxmax, bymin, bymax)
    _set_extent(ax, projection, extent, extrema)

    # Append a legend, if appropriate.
    if legend:
        _paint_colorbar_legend(ax, values, cmap, legend_kwargs)

    return ax


def cartogram(
    df, projection=None,
    scale=None, limits=(0.2, 1), scale_func=None,
    trace=True, trace_kwargs=None,
    hue=None, scheme=None, k=5, cmap='viridis',
    legend=False, legend_values=None, legend_labels=None, legend_kwargs=None, legend_var="scale",
    extent=None, figsize=(8, 6), ax=None, **kwargs
):
    """
    Self-scaling area plot.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        The projection to use. For reference see
        `Working with Projections <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Working%20with%20Projections.ipynb>`_.
    scale : str or iterable, optional
        The column in the dataset (or an iterable of some other data) with which to scale output
        points. For reference see
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Scale>`_.
    limits : (min, max) tuple, optional
        The minimum and maximum scale limits.
    scale_func : ufunc, optional
        The function used to scale point sizes.
    trace : boolean, optional
        Whether or not to include a trace of the polygon's original outline in the plot result.
    trace_kwargs : dict, optional
        If ``trace`` is set to ``True``, this parameter can be used to adjust the properties of the
        trace outline. This parameter is ignored if trace is ``False``.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The column in the dataset (or an iterable of some other data) used to color the points.
        For reference see
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Hue>`_.
    scheme : None or {"quantiles"|"equal_interval"|"fisher_jenks"}, optional
        If ``hue`` is specified, the map classifier to use.
    k : int or None, optional
        Ignored if ``hue`` is left unspecified. Otherwise, if ``categorical`` is False, controls
        how many colors to use (5 is the default). If set to ``None``, a continuous colormap will
        be used.
    cmap : matplotlib color, optional
        If ``hue`` is specified, the
        `matplotlib colormap <http://matplotlib.org/examples/color/colormaps_reference.html>`_ to use.
    legend : boolean, optional
        Whether or not to include a legend. Ignored if neither a ``hue`` nor a ``scale`` is
        specified.
    legend_values : list, optional
        The values to use in the legend. Defaults to equal intervals. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_labels : list, optional
        The names to use in the legend. Defaults to the variable values. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_kwargs : dict, optional
        Keyword arguments to be passed to 
        `the underlying legend <http://matplotlib.org/users/legend_guide.html>`_.
    extent : None or (min_longitude, max_longitude, min_latitude, max_latitude), optional
        Controls the plot extents. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the
        resultant plot.
    ax : AxesSubplot or GeoAxesSubplot instance, optional
        A ``matplotlib.axes.AxesSubplot`` or ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance.
        Defaults to a new axis.
    kwargs: dict, optional
        Keyword arguments to be passed to the underlying ``matplotlib`` `Polygon patches
        <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_.

    Returns
    -------
    ``AxesSubplot`` or ``GeoAxesSubplot``
        The plot axis

    Examples
    --------
    A cartogram is a plot type which ingests a series of enclosed ``Polygon`` or ``MultiPolygon``
    entities and spits out a view of these shapes in which area is distorted according to the size
    of some parameter of interest.

    A basic cartogram specifies data, a projection, and a ``scale`` parameter.

    .. code-block:: python

        import geoplot as gplt
        import geoplot.crs as gcrs
        gplt.cartogram(boroughs, scale='Population Density', projection=gcrs.AlbersEqualArea())

    .. image:: ../figures/cartogram/cartogram-initial.png

    The gray outline can be turned off by specifying ``trace``, and a legend can be added by
    specifying ``legend``.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=gcrs.AlbersEqualArea(),
                       trace=False, legend=True)

    .. image:: ../figures/cartogram/cartogram-trace-legend.png

    Keyword arguments can be passed to the legend using the ``legend_kwargs`` argument. These
    arguments will be passed to the underlying ``matplotlib.legend.Legend`` instance (`ref
    <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_). The ``loc`` and
    ``bbox_to_anchor`` parameters are particularly useful for positioning the legend. Other
    additional arguments will be passed to the underlying ``matplotlib``
    `scatter plot <http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.scatter>`_.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=gcrs.AlbersEqualArea(),
                       trace=False, legend=True, legend_kwargs={'loc': 'upper left'})

    .. image:: ../figures/cartogram/cartogram-legend-kwargs.png

    Additional arguments to ``cartogram`` will be interpreted as keyword arguments for the scaled
    polygons, using `matplotlib Polygon patch
    <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_ rules.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=gcrs.AlbersEqualArea(),
                       edgecolor='darkgreen')

    .. image:: ../figures/cartogram/cartogram-kwargs.png

    Manipulate the outlines use the ``trace_kwargs`` argument, which accepts the same 
    `matplotlib Polygon patch <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_
    parameters.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=gcrs.AlbersEqualArea(),
                       trace_kwargs={'edgecolor': 'lightgreen'})

    .. image:: ../figures/cartogram/cartogram-trace-kwargs.png

    Adjust the level of scaling to apply using the ``limits`` parameter.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=gcrs.AlbersEqualArea(),
                       limits=(0.5, 1))

    .. image:: ../figures/cartogram/cartogram-limits.png

    The default scaling function is linear: an observations at the midpoint of two others will be
    exactly midway between them in size. To specify an alternative scaling function, use the
    ``scale_func`` parameter. This should be a factory function of two variables which, when
    given the maximum and minimum of the dataset, returns a scaling function which will be applied
    to the rest of the data. A demo is available in the
    `example gallery <examples/usa-city-elevations.html>`_.

    .. code-block:: python

        def trivial_scale(minval, maxval): return lambda v: 2
        gplt.cartogram(boroughs, scale='Population Density', projection=gcrs.AlbersEqualArea(),
                       limits=(0.5, 1), scale_func=trivial_scale)

    .. image:: ../figures/cartogram/cartogram-scale-func.png

    ``cartogram`` also provides the same ``hue`` visual variable parameters provided by
    e.g. ``pointplot``. For more information on ``hue``-related arguments, see the related sections
    in the ``pointplot`` `documentation <./pointplot.html>`_.

    .. code-block:: python

        gplt.cartogram(boroughs, scale='Population Density', projection=gcrs.AlbersEqualArea(),
                       hue='Population Density', k=None, cmap='Blues')

    .. image:: ../figures/cartogram/cartogram-hue.png
    """
    # Initialize the figure.
    _init_figure(ax, figsize)

    # Load the projection.
    if projection:
        projection = projection.load(df, {
            'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
            'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
        })

        # Set up the axis.
        if not ax:
            ax = plt.subplot(111, projection=projection)

        # Clean up patches.
    else:
        if not ax:
            ax = plt.gca()

    # Clean up patches.
    _lay_out_axes(ax, projection)

    # Immediately return if input geometry is empty.
    if len(df.geometry) == 0:
        return ax

    # Set extent.
    extrema = _get_envelopes_min_maxes(df.geometry.envelope.exterior)
    _set_extent(ax, projection, extent, extrema)

    # Standardize hue and scale input.
    hue = _to_geoseries(df, hue)
    if not scale:
        raise ValueError("No scale parameter provided.")
    values = _to_geoseries(df, scale)

    # Compute a scale function.
    dmin, dmax = np.min(values), np.max(values)
    if not scale_func:
        dslope = (limits[1] - limits[0]) / (dmax - dmin)
        dscale = lambda dval: limits[0] + dslope * (dval - dmin)
    else:
        dscale = scale_func(dmin, dmax)

    # Create a legend, if appropriate.
    if legend:
        _paint_carto_legend(ax, values, legend_values, legend_labels, dscale, legend_kwargs)

    # Generate the coloring information, if needed. Follows one of two schemes,
    # categorical or continuous, based on whether or not ``k`` is specified (``hue`` must be
    # specified for either to work).
    if k is not None and hue is not None:
        # Categorical colormap code path.
        categorical, scheme = _validate_buckets(hue, scheme)

        if hue is not None:
            cmap, categories, hue_values = _discrete_colorize(
                categorical, hue, scheme, k, cmap,
            )
            colors = [cmap.to_rgba(v) for v in hue_values]

            # Add a legend, if appropriate.
            if legend and (legend_var != "scale" or scale is None):
                _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs)
        else:
            colors = ['None']*len(df)
    elif k is None and hue is not None:
        # Continuous colormap code path.
        hue_values = hue
        cmap = _continuous_colormap(hue_values, cmap,)
        colors = [cmap.to_rgba(v) for v in hue_values]

        # Add a legend, if appropriate.
        if legend and (legend_var != "scale" or scale is None):
            _paint_colorbar_legend(ax, hue_values, cmap, legend_kwargs)
    elif 'facecolor' in kwargs:
        colors = [kwargs.pop('facecolor')]*len(df)
    else:
        colors = ['None']*len(df)

    # Manipulate trace_kwargs.
    if trace:
        if trace_kwargs is None:
            trace_kwargs = dict()
        if 'edgecolor' not in trace_kwargs.keys():
            trace_kwargs['edgecolor'] = 'lightgray'
        if 'facecolor' not in trace_kwargs.keys():
            trace_kwargs['facecolor'] = 'None'

    # Draw traces first, if appropriate.
    if trace:
        if projection:
            for polygon in df.geometry:
                features = ShapelyFeature([polygon], ccrs.PlateCarree())
                ax.add_feature(features, **trace_kwargs)
        else:
            for polygon in df.geometry:
                try:  # Duck test for MultiPolygon.
                    for subgeom in polygon:
                        feature = descartes.PolygonPatch(subgeom, **trace_kwargs)
                        ax.add_patch(feature)
                except (TypeError, AssertionError):  # Shapely Polygon.
                    feature = descartes.PolygonPatch(polygon, **trace_kwargs)
                    ax.add_patch(feature)

    # Finally, draw the scaled geometries.
    for value, color, polygon in zip(values, colors, df.geometry):
        scale_factor = dscale(value)
        scaled_polygon = shapely.affinity.scale(polygon, xfact=scale_factor, yfact=scale_factor)
        if projection:
            features = ShapelyFeature([scaled_polygon], ccrs.PlateCarree())
            ax.add_feature(features, facecolor=color, **kwargs)
        else:
            try:  # Duck test for MultiPolygon.
                for subgeom in scaled_polygon:
                    feature = descartes.PolygonPatch(subgeom, facecolor=color, **kwargs)
                    ax.add_patch(feature)
            except (TypeError, AssertionError):  # Shapely Polygon.
                feature = descartes.PolygonPatch(scaled_polygon, facecolor=color, **kwargs)
                ax.add_patch(feature)

    return ax


def kdeplot(df, projection=None, extent=None, figsize=(8, 6), ax=None, clip=None, **kwargs):
    """
    Spatial kernel density estimate plot.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        The projection to use. For reference see
        `Working with Projections <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Working%20with%20Projections.ipynb>`_.
    clip : None or iterable or GeoSeries, optional
        If specified, the ``kdeplot`` output will be clipped to the boundaries of this geometry.
    extent : None or (min_longitude, max_longitude, min_latitude, max_latitude), optional
        Controls the plot extents. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the
        resultant plot.
    ax : AxesSubplot or GeoAxesSubplot instance, optional
        A ``matplotlib.axes.AxesSubplot`` or ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance.
        Defaults to a new axis.
    kwargs: dict, optional
        Keyword arguments to be passed to the underlying ``seaborn`` `kernel density estimate plot
        <https://seaborn.pydata.org/generated/seaborn.kdeplot.html>`_.

    Returns
    -------
    ``AxesSubplot`` or ``GeoAxesSubplot``
        The plot axis

    Examples
    --------
    `Kernel density estimate <https://en.wikipedia.org/wiki/Kernel_density_estimation>`_ is a
    flexible unsupervised machine learning technique for non-parametrically estimating the
    distribution underlying input data. The KDE is a great way of smoothing out random noise and
    estimating the  true shape of point data distributed in your space, but it needs a moderately
    large number of observations to be reliable.

    The ``geoplot`` ``kdeplot``, actually a thin wrapper on top of the ``seaborn`` ``kdeplot``,
    is an application of this visualization technique to the geospatial setting.

    A basic ``kdeplot`` specifies (pointwise) data and, optionally, a projection. To make the
    result more interpretable, I also overlay the underlying borough geometry.

    .. code-block:: python

        ax = gplt.kdeplot(collisions, projection=gcrs.AlbersEqualArea())
        gplt.polyplot(boroughs, projection=gcrs.AlbersEqualArea(), ax=ax)

    .. image:: ../figures/kdeplot/kdeplot-overlay.png

    Most of the rest of the parameters to ``kdeplot`` are parameters inherited from
    `the seaborn method by the same name <http://seaborn.pydata.org/generated/seaborn.kdeplot.html#seaborn.kdeplot>`_,
    on which this plot type is based. For example, specifying ``shade=True`` provides a filled
    KDE instead of a contour one:

    .. code-block:: python

        ax = gplt.kdeplot(collisions, projection=gcrs.AlbersEqualArea(),
                          shade=True)
        gplt.polyplot(boroughs, projection=gcrs.AlbersEqualArea(), ax=ax)

    .. image:: ../figures/kdeplot/kdeplot-shade.png

    Use ``n_levels`` to specify the number of contour levels.

    .. code-block:: python

        ax = gplt.kdeplot(collisions, projection=gcrs.AlbersEqualArea(),
                          n_levels=30)
        gplt.polyplot(boroughs, projection=gcrs.AlbersEqualArea(), ax=ax)

    .. image:: ../figures/kdeplot/kdeplot-n-levels.png

    Or specify ``cmap`` to change the colormap.

    .. code-block:: python

        ax = gplt.kdeplot(collisions, projection=gcrs.AlbersEqualArea(),
             cmap='Purples')
        gplt.polyplot(boroughs, projection=gcrs.AlbersEqualArea(), ax=ax)

    .. image:: ../figures/kdeplot/kdeplot-cmap.png

    Oftentimes given the geometry of the location, a "regular" continuous KDEPlot doesn't make
    sense. We can specify a ``clip`` of iterable geometries, which will be used to trim the
    ``kdeplot``. Note that if you have set ``shade=True`` as a parameter you may need to
    additionally specify ``shade_lowest=False`` to avoid inversion at the edges of the plot.

    .. code-block:: python

        gplt.kdeplot(collisions, projection=gcrs.AlbersEqualArea(),
                     shade=True, clip=boroughs)

    .. image:: ../figures/kdeplot/kdeplot-clip.png

    """
    import seaborn as sns  # Immediately fail if no seaborn.

    # Initialize the figure.
    _init_figure(ax, figsize)

    # Necessary prior.
    xs = np.array([p.x for p in df.geometry])
    ys = np.array([p.y for p in df.geometry])

    # Load the projection.
    if projection:
        projection = projection.load(df, {
            'central_longitude': lambda df: np.mean(xs),
            'central_latitude': lambda df: np.mean(ys)
        })

        # Set up the axis.
        if not ax:
            ax = plt.subplot(111, projection=projection)
    else:
        if not ax:
            ax = plt.gca()

    # Clean up patches.
    _lay_out_axes(ax, projection)

    # Immediately return if input geometry is empty.
    if len(df.geometry) == 0:
        return ax

    # Set extent.
    extrema = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
    _set_extent(ax, projection, extent, extrema)

    if projection:
        if clip is None:
            sns.kdeplot(
                pd.Series([p.x for p in df.geometry]),
                pd.Series([p.y for p in df.geometry]),
                transform=ccrs.PlateCarree(), ax=ax, **kwargs
            )
        else:
            sns.kdeplot(
                pd.Series([p.x for p in df.geometry]),
                pd.Series([p.y for p in df.geometry]),
                transform=ccrs.PlateCarree(), ax=ax, **kwargs
            )
            clip_geom = _get_clip(ax.get_extent(crs=ccrs.PlateCarree()), clip)
            feature = ShapelyFeature([clip_geom], ccrs.PlateCarree())
            ax.add_feature(feature, facecolor=(1,1,1), linewidth=0, zorder=100)
    else:
        if clip is None:
            sns.kdeplot(
                pd.Series([p.x for p in df.geometry]),
                pd.Series([p.y for p in df.geometry]),
                ax=ax, **kwargs
            )
        else:
            clip_geom = _get_clip(ax.get_xlim() + ax.get_ylim(), clip)
            polyplot(gpd.GeoSeries(clip_geom),
                     facecolor='white', linewidth=0, zorder=100, 
                     extent=ax.get_xlim() + ax.get_ylim(), ax=ax)
            sns.kdeplot(
                pd.Series([p.x for p in df.geometry]),
                pd.Series([p.y for p in df.geometry]),
                ax=ax, **kwargs
            )
    return ax


def sankey(
    *args, projection=None,
    start=None, end=None, path=None,
    hue=None, scheme=None, k=5, cmap='viridis',
    legend=False, legend_kwargs=None, legend_labels=None, legend_values=None, legend_var=None,
    extent=None, figsize=(8, 6),
    scale=None, scale_func=None, limits=(1, 5),
    ax=None, **kwargs
):
    """
    Spatial Sankey or flow map.

    Parameters
    ----------
    df : GeoDataFrame, optional.
        The data being plotted. This parameter is optional - it is not needed if ``start`` and
        ``end`` (and ``hue``, if provided) are iterables.
    projection : geoplot.crs object instance, optional
        The projection to use. For reference see
        `Working with Projections <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Working%20with%20Projections.ipynb>`_.
    start : str or iterable
        A list of starting points. This parameter is required.
    end : str or iterable
        A list of ending points. This parameter is required.
    path : geoplot.crs object instance or iterable, optional
        Pass an iterable of paths to draw custom paths (see `this example
        <https://residentmario.github.io/geoplot/examples/dc-street-network.html>`_), or a
        projection to draw the shortest paths in that given projection. The default is
        ``Geodetic()``, which will connect points using 
        `great circle distance <https://en.wikipedia.org/wiki/Great-circle_distance>`_—the true
        shortest path on the surface of the Earth.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The column in the dataset (or an iterable of some other data) used to color the points.
        For reference see
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Hue>`_.
    scheme : None or {"quantiles"|"equal_interval"|"fisher_jenks"}, optional
        If ``hue`` is specified, the map classifier to use.
    k : int or None, optional
        Ignored if ``hue`` is left unspecified. Otherwise, if ``categorical`` is False, controls
        how many colors to use (5 is the default). If set to ``None``, a continuous colormap will
        be used.
    cmap : matplotlib color, optional
        If ``hue`` is specified, the
        `matplotlib colormap <http://matplotlib.org/examples/color/colormaps_reference.html>`_ to use.
    scale : str or iterable, optional
        The column in the dataset (or an iterable of some other data) with which to scale output
        points. For reference see
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Scale>`_.
    limits : (min, max) tuple, optional
        The minimum and maximum scale limits.
    scale_func : ufunc, optional
        The function used to scale point sizes.
    legend : boolean, optional
        Whether or not to include a legend. Ignored if neither a ``hue`` nor a ``scale`` is
        specified.
    legend_values : list, optional
        The values to use in the legend. Defaults to equal intervals. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_labels : list, optional
        The names to use in the legend. Defaults to the variable values. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_var : "hue" or "scale", optional
        Which variable (``hue`` or ``scale``) to use in the legend.
    legend_kwargs : dict, optional
        Keyword arguments to be passed to 
        `the underlying legend <http://matplotlib.org/users/legend_guide.html>`_.
    extent : None or (min_longitude, max_longitude, min_latitude, max_latitude), optional
        Controls the plot extents. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the
        resultant plot.
    ax : AxesSubplot or GeoAxesSubplot instance, optional
        A ``matplotlib.axes.AxesSubplot`` or ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance.
        Defaults to a new axis.
    kwargs: dict, optional
        Keyword arguments to be passed to the underlying ``matplotlib`` 
        `Line2D <https://matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D>`_
        instances.

    Returns
    -------
    ``AxesSubplot`` or ``GeoAxesSubplot``
        The plot axis

    Examples
    --------
    A `Sankey diagram <https://en.wikipedia.org/wiki/Sankey_diagram>`_ is a simple visualization
    demonstrating flow through a network. A Sankey diagram is useful when you wish to show the
    volume of things moving between points or spaces: traffic load a road network, for example, or
    inter-airport travel volumes. The ``geoplot`` ``sankey`` adds spatial context to this plot type
    by laying out the points in meaningful locations: airport locations, say, or road
    intersections.

    A basic ``sankey`` specifies data, ``start`` points, ``end`` points, and, optionally, a
    projection. The ``df`` argument is optional; if geometries are provided as independent
    iterables it is ignored. We overlay world geometry to aid interpretability.

    .. code-block:: python

        ax = gplt.sankey(la_flights, start='start', end='end', projection=gcrs.PlateCarree())
        ax.set_global(); ax.coastlines()

    .. image:: ../figures/sankey/sankey-geospatial-context.png

    The lines appear curved because they are 
    `great circle <https://en.wikipedia.org/wiki/Great-circle_distance>`_ paths, which are the
    shortest routes between points on a sphere.

    .. code-block:: python

        ax = gplt.sankey(la_flights, start='start', end='end', projection=gcrs.Orthographic())
        ax.set_global(); ax.coastlines(); ax.outline_patch.set_visible(True)

    .. image:: ../figures/sankey/sankey-greatest-circle-distance.png

    To plot using a different distance metric pass a ``cartopy`` ``crs`` object (*not* a 
    ``geoplot`` one) to the ``path`` parameter.

    .. code-block:: python

        import cartopy.crs as ccrs
        ax = gplt.sankey(la_flights, start='start', end='end', projection=gcrs.PlateCarree(),
                         path=ccrs.PlateCarree())
        ax.set_global(); ax.coastlines()

    .. image:: ../figures/sankey/sankey-path-projection.png

    If your data has custom paths, you can use those instead, via the ``path`` parameter.

    .. code-block:: python

        gplt.sankey(dc, path=dc.geometry, projection=gcrs.AlbersEqualArea(), scale='aadt')


    .. image:: ../figures/sankey/sankey-path.png

    ``hue`` parameterizes the color, and ``cmap`` controls the colormap. ``legend`` adds a legend.
    Keyword arguments can be passed to the legend using the ``legend_kwargs`` argument. These
    arguments will be passed to the underlying ``matplotlib`` `Legend
    <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_. The ``loc`` and
    ``bbox_to_anchor`` parameters are particularly useful for positioning the legend.

    .. code-block:: python

        ax = gplt.sankey(network, projection=gcrs.PlateCarree(),
                         start='from', end='to',
                         hue='mock_variable', cmap='RdYlBu',
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.4, 1.0)})
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-legend-kwargs.png

    Change the number of bins by specifying an alternative ``k`` value. To use a continuous
    colormap, explicitly specify ``k=None``. You can change the binning sceme with ``scheme``.
    The default is ``quantile``, which bins observations into classes of different sizes but the
    same numbers of observations. ``equal_interval`` will creates bins that are the same size, but
    potentially containing different numbers of observations. The more complicated ``fisher_jenks``
    scheme is an intermediate between the two.

    .. code-block:: python

        ax = gplt.sankey(network, projection=gcrs.PlateCarree(),
                         start='from', end='to',
                         hue='mock_variable', cmap='RdYlBu',
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.25, 1.0)},
                         k=3, scheme='equal_interval')
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-scheme.png

    ``geoplot`` will automatically do the right thing if your variable of interest is already
    `categorical <http://pandas.pydata.org/pandas-docs/stable/categorical.html>`_:

    .. code-block:: python

        ax = gplt.sankey(network, projection=gcrs.PlateCarree(),
                         start='from', end='to',
                         hue='above_meridian', cmap='RdYlBu',
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.2, 1.0)})
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-categorical.png

    ``scale`` can be used to enable ``linewidth`` as a visual variable. Adjust the upper and lower
    bound with the ``limits`` parameter.

    .. code-block:: python

        ax = gplt.sankey(la_flights, projection=gcrs.PlateCarree(),
                         extent=(-125.0011, -66.9326, 24.9493, 49.5904),
                         start='start', end='end',
                         scale='Passengers',
                         limits=(0.1, 5),
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.1, 1.0)})
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-scale.png

    The default scaling function is linear: an observations at the midpoint of two others will be
    exactly midway between them in size. To specify an alternative scaling function, use the
    ``scale_func`` parameter. This should be a factory function of two variables which, when given
    the maximum and minimum of the dataset, returns a scaling function which will be applied to the
    rest of the data. A demo is available in the 
    `example gallery <examples/usa-city-elevations.html>`_.

    .. code-block:: python

        def trivial_scale(minval, maxval): return lambda v: 1
        ax = gplt.sankey(la_flights, projection=gcrs.PlateCarree(),
                         extent=(-125.0011, -66.9326, 24.9493, 49.5904),
                         start='start', end='end',
                         scale='Passengers', scale_func=trivial_scale,
                         legend=True, legend_kwargs={'bbox_to_anchor': (1.1, 1.0)})
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-scale-func.png

    ``hue`` and ``scale`` can co-exist. In case more than one visual variable is used, control
    which one appears in the legend using ``legend_var``.

    .. code-block:: python

        ax = gplt.sankey(network, projection=gcrs.PlateCarree(),
                 start='from', end='to',
                 scale='mock_data',
                 legend=True, legend_kwargs={'bbox_to_anchor': (1.1, 1.0)},
                 hue='mock_data', legend_var="hue")
        ax.set_global()
        ax.coastlines()

    .. image:: ../figures/sankey/sankey-legend-var.png

    """
    # Validate df.
    if len(args) > 1:
        raise ValueError("Invalid input.")
    elif len(args) == 1:
        df = args[0]
    else:
        df = pd.DataFrame()
        # df = None  # bind the local name here; initialize in a bit.

    # Validate the rest of the input.
    if ((start is None) or (end is None)) and not hasattr(path, "__iter__"):
        raise ValueError("The 'start' and 'end' parameters must both be specified.")
    if (isinstance(start, str) or isinstance(end, str)) and df.empty:
        raise ValueError("Invalid input.")
    if isinstance(start, str):
        start = df[start]
    elif start is not None:
        start = gpd.GeoSeries(start)
    if isinstance(end, str):
        end = df[end]
    elif end is not None:
        end = gpd.GeoSeries(end)
    if (start is not None) and (end is not None) and hasattr(path, "__iter__"):
        raise ValueError(
            "One of 'start' and 'end' OR 'path' must be specified, but they cannot be specified "
            "simultaneously."
        )
    if path is None:  # No path provided.
        path = ccrs.Geodetic()
        path_geoms = None
    elif isinstance(path, str):  # Path is a column in the dataset.
        path_geoms = df[path]
    elif hasattr(path, "__iter__"):  # Path is an iterable.
        path_geoms = gpd.GeoSeries(path)
    else:  # Path is a cartopy.crs object.
        path_geoms = None
    if start is not None and end is not None:
        points = pd.concat([start, end])
    else:
        points = None

    # Set legend variable.
    legend_var = _set_legend_var(legend_var, hue, scale)

    # After validating the inputs, we are in one of two modes:
    # (1) Projective mode. In this case ``path_geoms`` is None, while ``points`` contains a
    # concatenation of our points (for use in initializing the plot extents). This case occurs
    # when the user specifies ``start`` and ``end``, and not ``path``. This is "projective mode"
    # because it means that ``path`` will be a projection---if one is not provided explicitly, the
    # ``gcrs.Geodetic()`` projection.
    # (2) Path mode. In this case ``path_geoms`` is an iterable of LineString entities to be
    # plotted, while ``points`` is None. This occurs when the user specifies ``path``, and not
    # ``start`` or ``end``. This is path mode because we will need to plot exactly those paths!

    # At this point we'll initialize the rest of the variables we need. The way that we initialize
    # them is going to depend on which code path we are on. Additionally, we will initialize the
    # `df` variable with a projection dummy, if it has not been initialized already. This `df`
    # will only be used for figuring out the extent, and will be discarded afterwards!
    #
    # Variables we need to generate at this point, and why we need them:
    # 1. (clong, clat) --- To pass this to the projection settings.
    # 2. (xmin. xmax, ymin. ymax) --- To pass this to the extent settings.
    # 3. n --- To pass this to the color array in case no ``color`` is specified.
    if path_geoms is None and points is not None:
        if df.empty:
            df = gpd.GeoDataFrame(geometry=points)
        xs = np.array([p.x for p in points])
        ys = np.array([p.y for p in points])
        xmin, xmax, ymin, ymax = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
        clong, clat = np.mean(xs), np.mean(ys)
        n = int(len(points) / 2)
    else:  # path_geoms is an iterable
        path_geoms = gpd.GeoSeries(path_geoms)
        xmin, xmax, ymin, ymax = _get_envelopes_min_maxes(path_geoms.envelope.exterior)
        clong, clat = (xmin + xmax) / 2, (ymin + ymax) / 2
        n = len(path_geoms)

    # Initialize the figure.
    _init_figure(ax, figsize)

    # Load the projection.
    if projection:
        projection = projection.load(df, {
            'central_longitude': lambda df: clong,
            'central_latitude': lambda df: clat
        })

        # Set up the axis.
        if not ax:
            ax = plt.subplot(111, projection=projection)
    else:
        if not ax:
            ax = plt.gca()

    # Clean up patches.
    _lay_out_axes(ax, projection)

    # Set extent.
    if projection:
        if extent:
            ax.set_extent(extent)
        else:
            ax.set_extent((xmin, xmax, ymin, ymax))
    else:
        if extent:
            ax.set_xlim((extent[0], extent[1]))
            ax.set_ylim((extent[2], extent[3]))
        else:
            ax.set_xlim((xmin, xmax))
            ax.set_ylim((ymin, ymax))

    # Generate the coloring information, if needed. Follows one of two schemes,
    # categorical or continuous, based on whether or not ``k`` is specified (``hue`` must be
    # specified for either to work).
    if k is not None:
        # Categorical colormap code path.
        categorical, scheme = _validate_buckets(hue, scheme)

        hue = _to_geoseries(df, hue)

        if hue is not None:
            cmap, categories, hue_values = _discrete_colorize(
                categorical, hue, scheme, k, cmap,
            )
            colors = [cmap.to_rgba(v) for v in hue_values]

            # Add a legend, if appropriate.
            if legend and (legend_var != "scale" or scale is None):
                _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs)
        else:
            if 'color' not in kwargs.keys():
                colors = ['steelblue'] * n
            else:
                colors = [kwargs['color']] * n
                kwargs.pop('color')
    elif k is None and hue is not None:
        # Continuous colormap code path.
        hue_values = hue
        cmap = _continuous_colormap(hue_values, cmap)
        colors = [cmap.to_rgba(v) for v in hue_values]

        # Add a legend, if appropriate.
        if legend and (legend_var != "scale" or scale is None):
            _paint_colorbar_legend(ax, hue_values, cmap, legend_kwargs)

    # Check if the ``scale`` parameter is filled, and use it to fill a ``values`` name.
    if scale is not None:
        scalar_values = _to_geoseries(df, scale)

        # Compute a scale function.
        dmin, dmax = np.min(scalar_values), np.max(scalar_values)
        if not scale_func:
            dslope = (limits[1] - limits[0]) / (dmax - dmin)
            dscale = lambda dval: limits[0] + dslope * (dval - dmin)
        else:
            dscale = scale_func(dmin, dmax)

        # Apply the scale function.
        scalar_multiples = np.array([dscale(d) for d in scalar_values])
        widths = scalar_multiples * 1

        # Draw a legend, if appropriate.
        if legend and (legend_var == "scale"):
            _paint_carto_legend(
                ax, scalar_values, legend_values, legend_labels, dscale, legend_kwargs
            )
    else:
        widths = [1] * n  # pyplot default

    # Allow overwriting visual arguments.
    if 'linestyle' in kwargs.keys():
        linestyle = kwargs['linestyle']; kwargs.pop('linestyle')
    else:
        linestyle = '-'
    if 'color' in kwargs.keys():
        colors = [kwargs['color']]*n; kwargs.pop('color')
    # plt.plot uses 'color', mpl.ax.add_feature uses 'edgecolor'. Support both.
    elif 'edgecolor' in kwargs.keys():
        colors = [kwargs['edgecolor']]*n; kwargs.pop('edgecolor')
    if 'linewidth' in kwargs.keys():
        widths = [kwargs['linewidth']]*n; kwargs.pop('linewidth')

    if projection:
        # Duck test plot. The first will work if a valid transformation is passed to ``path``
        # (e.g. we are in the ``start + ``end`` case), the second will work if ``path`` is an
        # iterable (e.g. we are in the ``path`` case).
        try:
            for origin, destination, color, width in zip(start, end, colors, widths):
                ax.plot([origin.x, destination.x], [origin.y, destination.y], transform=path,
                        linestyle=linestyle, linewidth=width, color=color, **kwargs)
        except TypeError:
            for line, color, width in zip(path_geoms, colors, widths):
                feature = ShapelyFeature([line], ccrs.PlateCarree())
                ax.add_feature(
                    feature, linestyle=linestyle, linewidth=width, edgecolor=color,
                    facecolor='None', **kwargs
                )
    else:
        try:
            for origin, destination, color, width in zip(start, end, colors, widths):
                ax.plot([origin.x, destination.x], [origin.y, destination.y],
                        linestyle=linestyle, linewidth=width, color=color, **kwargs)
        except TypeError:
            for path, color, width in zip(path_geoms, colors, widths):
                # We have to implement different methods for dealing with LineString and
                # MultiLineString objects. This calls for, yep, another duck test.
                try:  # LineString
                    line = mpl.lines.Line2D([coord[0] for coord in path.coords],
                                            [coord[1] for coord in path.coords],
                                            linestyle=linestyle, linewidth=width, color=color,
                                            **kwargs)
                    ax.add_line(line)
                except NotImplementedError:  # MultiLineString
                    for line in path:
                        line = mpl.lines.Line2D([coord[0] for coord in line.coords],
                                                [coord[1] for coord in line.coords],
                                                linestyle=linestyle, linewidth=width, color=color,
                                                **kwargs)
                        ax.add_line(line)
    return ax


def voronoi(
    df, projection=None, clip=None,
    cmap='viridis', hue=None, scheme=None, k=5,
    legend=False, legend_kwargs=None, legend_labels=None,
    extent=None, edgecolor='black', figsize=(8, 6), ax=None, **kwargs
):
    """
    Geospatial Voronoi diagram.

    Parameters
    ----------
    df : GeoDataFrame
        The data being plotted.
    projection : geoplot.crs object instance, optional
        The projection to use. For reference see
        `Working with Projections <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Working%20with%20Projections.ipynb>`_.
    hue : None, Series, GeoSeries, iterable, or str, optional
        The column in the dataset (or an iterable of some other data) used to color the points.
        For reference see
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Hue>`_.
    scheme : None or {"quantiles"|"equal_interval"|"fisher_jenks"}, optional
        If ``hue`` is specified, the map classifier to use.
    k : int or None, optional
        Ignored if ``hue`` is left unspecified. Otherwise, if ``categorical`` is False, controls
        how many colors to use (5 is the default). If set to ``None``, a continuous colormap
        will be used.
    cmap : matplotlib color, optional
        If ``hue`` is specified, the
        `matplotlib colormap <http://matplotlib.org/examples/color/colormaps_reference.html>`_ to use.
    legend : boolean, optional
        Whether or not to include a legend. Ignored if neither a ``hue`` nor a ``scale`` is
        specified.
    legend_values : list, optional
        The values to use in the legend. Defaults to equal intervals. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_labels : list, optional
        The names to use in the legend. Defaults to the variable values. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb#Legend>`_.
    legend_kwargs : dict, optional
        Keyword arguments to be passed to 
        `the underlying legend <http://matplotlib.org/users/legend_guide.html>`_.
    extent : None or (min_longitude, max_longitude, min_latitude, max_latitude), optional
        Controls the plot extents. For reference see 
        `Customizing Plots <https://nbviewer.jupyter.org/github/ResidentMario/geoplot/blob/master/notebooks/tutorials/Customizing%20Plots.ipynb>`_.
    figsize : tuple, optional
        An (x, y) tuple passed to ``matplotlib.figure`` which sets the size, in inches, of the
        resultant plot.
    ax : AxesSubplot or GeoAxesSubplot instance, optional
        A ``matplotlib.axes.AxesSubplot`` or ``cartopy.mpl.geoaxes.GeoAxesSubplot`` instance.
        Defaults to a new axis.
    kwargs: dict, optional
        Keyword arguments to be passed to the underlying ``matplotlib`` `Line2D objects
        <http://matplotlib.org/api/lines_api.html#matplotlib.lines.Line2D>`_.

    Returns
    -------
    AxesSubplot or GeoAxesSubplot instance
        The axis object with the plot on it.

    Examples
    --------

    The neighborhood closest to a point in space is known as its `Voronoi region
    <https://en.wikipedia.org/wiki/Voronoi_diagram>`_. Every point in a dataset has a Voronoi
    region, which may be either a closed polygon (for inliers) or open infinite region (for points
    on the edge of the distribution). A Voronoi diagram works by dividing a space filled with
    points into such regions and plotting the result. Voronoi plots allow efficient assessment of
    the *density* of points in different spaces, and when combined with a colormap can be quite
    informative of overall trends in the dataset.

    The ``geoplot`` ``voronoi`` is a spatially aware application of this technique. It compares
    well with the more well-known ``choropleth``, which has the advantage of using meaningful
    regions, but the disadvantage of having defined those regions beforehand. ``voronoi`` has
    fewer requirements and may perform better when the number of observations is small. Compare
    also with the quadtree technique available in ``aggplot``.

    A basic ``voronoi`` specified data and, optionally, a projection. We overlay geometry to aid
    interpretability.

    .. code-block:: python

        ax = gplt.voronoi(injurious_collisions.head(1000))
        gplt.polyplot(boroughs, ax=ax)

    .. image:: ../figures/voronoi/voronoi-simple.png

    ``hue`` parameterizes the color, and ``cmap`` controls the colormap.

    .. code-block:: python

        ax = gplt.voronoi(injurious_collisions.head(1000), hue='NUMBER OF PERSONS INJURED',
                          cmap='Reds')
        gplt.polyplot(boroughs, ax=ax)

    .. image:: ../figures/voronoi/voronoi-cmap.png

    Add a ``clip`` of iterable geometries to trim the ``voronoi`` against local geography.

    .. code-block:: python

        ax = gplt.voronoi(injurious_collisions.head(1000), hue='NUMBER OF PERSONS INJURED',
                          cmap='Reds', clip=boroughs.geometry)
        gplt.polyplot(boroughs, ax=ax)

    .. image:: ../figures/voronoi/voronoi-clip.png

    ``legend`` adds a a ``matplotlib`` `Legend
    <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_. This can be tuned
    even further using the ``legend_kwargs`` argument. Other keyword parameters are passed to the
    underlying ``matplotlib``
    `Polygon patches <http://matplotlib.org/api/patches_api.html#matplotlib.patches.Polygon>`_.

    .. code-block:: python

        ax = gplt.voronoi(injurious_collisions.head(1000), hue='NUMBER OF PERSONS INJURED',
                          cmap='Reds',
                          clip=boroughs.geometry,
                          legend=True, legend_kwargs={'loc': 'upper left'},
                          linewidth=0.5, edgecolor='white')
        gplt.polyplot(boroughs, ax=ax)

    .. image:: ../figures/voronoi/voronoi-kwargs.png

    Change the number of bins by specifying an alternative ``k`` value. To use a continuous
    colormap, explicitly specify ``k=None``.  You can change the binning sceme with ``scheme``.
    The default is ``quantile``, which bins observations into classes of different sizes but the
    same numbers of observations. ``equal_interval`` will creates bins that are the same size, but
    potentially containing different numbers of observations. The more complicated ``fisher_jenks``
    scheme is an intermediate between the two.

    .. code-block:: python

        ax = gplt.voronoi(injurious_collisions.head(1000),
                          hue='NUMBER OF PERSONS INJURED', cmap='Reds', k=5, scheme='fisher_jenks',
                          clip=boroughs.geometry,
                          legend=True, legend_kwargs={'loc': 'upper left'},
                          linewidth=0.5, edgecolor='white',
                         )
        gplt.polyplot(boroughs, ax=ax)

    .. image:: ../figures/voronoi/voronoi-scheme.png

    ``geoplot`` will automatically do the right thing if your variable of interest is already
    `categorical <http://pandas.pydata.org/pandas-docs/stable/categorical.html>`_:

    .. code-block:: python

        ax = gplt.voronoi(injurious_collisions.head(1000), hue='NUMBER OF PERSONS INJURED',
                          cmap='Reds',
                          edgecolor='white', clip=boroughs.geometry,
                          linewidth=0.5)
        gplt.polyplot(boroughs, linewidth=1, ax=ax)

    .. image:: ../figures/voronoi/voronoi-multiparty.png
    """
    # Initialize the figure.
    _init_figure(ax, figsize)

    if projection:
        # Properly set up the projection.
        projection = projection.load(df, {
            'central_longitude': lambda df: np.mean(np.array([p.x for p in df.geometry.centroid])),
            'central_latitude': lambda df: np.mean(np.array([p.y for p in df.geometry.centroid]))
        })

        # Set up the axis.
        if not ax:
            ax = plt.subplot(111, projection=projection)

    else:
        if not ax:
            ax = plt.gca()

    # Clean up patches.
    _lay_out_axes(ax, projection)

    # Immediately return if input geometry is empty.
    if len(df.geometry) == 0:
        return ax

    # Set extent.
    xs, ys = [p.x for p in df.geometry.centroid], [p.y for p in df.geometry.centroid]
    extrema = np.min(xs), np.max(xs), np.min(ys), np.max(ys)
    _set_extent(ax, projection, extent, extrema)

    # Validate hue input.
    hue = _to_geoseries(df, hue)

    # Generate the coloring information, if needed. Follows one of two schemes,
    # categorical or continuous, based on whether or not ``k`` is specified (``hue`` must be
    # specified for either to work).
    if k is not None:
        # Categorical colormap code path.
        categorical, scheme = _validate_buckets(hue, scheme)

        if hue is not None:
            cmap, categories, hue_values = _discrete_colorize(
                categorical, hue, scheme, k, cmap
            )
            colors = [cmap.to_rgba(v) for v in hue_values]

        else:
            colors = ['None']*len(df)

    elif k is None and hue is not None:
        # Continuous colormap code path.
        hue_values = hue
        cmap = _continuous_colormap(hue_values, cmap)
        colors = [cmap.to_rgba(v) for v in hue_values]

    elif 'facecolor' in kwargs:
        colors = [kwargs.pop('facecolor')]*len(df)
    else:
        colors = ['None']*len(df)

    # Finally we draw the features.
    geoms = _build_voronoi_polygons(df)
    if projection:
        for color, geom in zip(colors, geoms):
            features = ShapelyFeature([geom], ccrs.PlateCarree())
            ax.add_feature(features, facecolor=color, edgecolor=edgecolor, **kwargs)

        if clip is not None:
            clip_geom = _get_clip(ax.get_extent(crs=ccrs.PlateCarree()), clip)
            feature = ShapelyFeature([clip_geom], ccrs.PlateCarree())
            ax.add_feature(feature, facecolor=(1,1,1), linewidth=0, zorder=100)

    else:
        for color, geom in zip(colors, geoms):
            feature = descartes.PolygonPatch(geom, facecolor=color, edgecolor=edgecolor, **kwargs)
            ax.add_patch(feature)

        if clip is not None:
            clip_geom = _get_clip(ax.get_xlim() + ax.get_ylim(), clip)
            ax = polyplot(gpd.GeoSeries(clip_geom), facecolor='white', linewidth=0, zorder=100,
                          extent=ax.get_xlim() + ax.get_ylim(), ax=ax)

    # Add a legend, if appropriate.
    if legend and k is not None:
        _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs, figure=True)
    elif legend and k is None and hue is not None:
        _paint_colorbar_legend(ax, hue_values, cmap, legend_kwargs)

    return ax


##################
# HELPER METHODS #
##################


def _init_figure(ax, figsize):
    """
    Initializes the ``matplotlib`` ``figure``, one of the first things that every plot must do. No
    figure is initialized (and, consequentially, the ``figsize`` argument is ignored) if a
    pre-existing ``ax`` is passed to the method. This is necessary for ``plt.savefig()`` to work.
    """
    if not ax:
        fig = plt.figure(figsize=figsize)
        return fig


def _get_envelopes_min_maxes(envelopes):
    """
    Returns the extrema of the inputted polygonal envelopes. Used for setting chart extent where
    appropriate. Note tha the ``Quadtree.bounds`` object property serves a similar role. Returns
    a (xmin, xmax, ymin, ymax) tuple of data extrema.
    """
    xmin = np.min(
        envelopes.map(
            lambda linearring: np.min([
                linearring.coords[1][0], linearring.coords[2][0], linearring.coords[3][0],
                linearring.coords[4][0]
            ])
        )
    )
    xmax = np.max(
        envelopes.map(
            lambda linearring: np.max([
                linearring.coords[1][0], linearring.coords[2][0], linearring.coords[3][0],
                linearring.coords[4][0]
            ])
        )
    )
    ymin = np.min(
        envelopes.map(
            lambda linearring: np.min([
                linearring.coords[1][1], linearring.coords[2][1], linearring.coords[3][1],
                linearring.coords[4][1]
            ])
        )
    )
    ymax = np.max(
        envelopes.map(
            lambda linearring: np.max([
                linearring.coords[1][1], linearring.coords[2][1], linearring.coords[3][1],
                linearring.coords[4][1]
            ])
        )
    )
    return xmin, xmax, ymin, ymax


def _get_envelopes_centroid(envelopes):
    """
    Returns the centroid of an inputted geometry column. Not currently in use, as this is now
    handled by this library's CRS wrapper directly. Light wrapper over
    ``_get_envelopes_min_maxes``. Returns (mean_x, mean_y), the data centroid.
    """
    xmin, xmax, ymin, ymax = _get_envelopes_min_maxes(envelopes)
    return np.mean(xmin, xmax), np.mean(ymin, ymax)


def _set_extent(ax, projection, extent, extrema):
    """
    Sets the plot extent.
    """
    if extent:
        xmin, xmax, ymin, ymax = extent
        xmin, xmax, ymin, ymax = max(xmin, -180), min(xmax, 180), max(ymin, -90), min(ymax, 90)

        if projection:  # input ``extent`` into set_extent().
            ax.set_extent((xmin, xmax, ymin, ymax), crs=ccrs.PlateCarree())
        else:  # input ``extent`` into set_ylim, set_xlim.
            ax.set_xlim((xmin, xmax))
            ax.set_ylim((ymin, ymax))

    else:
        xmin, xmax, ymin, ymax = extrema
        xmin, xmax, ymin, ymax = max(xmin, -180), min(xmax, 180), max(ymin, -90), min(ymax, 90)

        if projection:  # input ``extrema`` into set_extent.
            ax.set_extent((xmin, xmax, ymin, ymax), crs=ccrs.PlateCarree())
        else:  # input ``extrema`` into set_ylim, set_xlim.
            ax.set_xlim((xmin, xmax))
            ax.set_ylim((ymin, ymax))


def _lay_out_axes(ax, projection):
    """
    ``cartopy`` enables a a transparent background patch and an "outline" patch by default. This
    short method simply hides these extraneous visual features. If the plot is a pure
    ``matplotlib`` one, it does the same thing by removing the axis altogether.
    """
    if projection is not None:
        ax.background_patch.set_visible(False)
        ax.outline_patch.set_visible(False)
    else:
        plt.gca().axison = False


def _set_legend_var(legend_var, hue, scale):
    """
    Given ``hue`` and ``scale`` variables with mixed validity, returns the correct 
    ``legend_var``.
    """
    if legend_var is None:
        if hue is not None:
            legend_var = "hue"
        elif scale is not None:
            legend_var = "scale"
    return legend_var


def _to_geoseries(df, hue):
    """
    The top-level ``hue`` parameter present in most plot types accepts a variety of input types.
    This method condenses this variety into a single preferred format---an iterable---which is
    expected by all submethods working with the data downstream of it.
    """
    if hue is None:
        return None
    elif isinstance(hue, str):
        hue = df[hue]
        return hue
    else:
        return gpd.GeoSeries(hue)


def _continuous_colormap(hue, cmap):
    """
    Creates a continuous colormap.
    """
    mn = min(hue)
    mx = max(hue)
    norm = mpl.colors.Normalize(vmin=mn, vmax=mx)
    return mpl.cm.ScalarMappable(norm=norm, cmap=cmap)


def _discrete_colorize(categorical, hue, scheme, k, cmap):
    """
    Creates a discrete colormap, either using an already-categorical data variable or by bucketing
    a non-categorical ordinal one. If a scheme is provided we compute a distribution for the given
    data. If one is not provided we assume that the input data is categorical.
    """
    if not categorical:
        binning = _mapclassify_choro(hue, scheme, k=k)
        values = binning.yb
        binedges = [binning.yb.min()] + binning.bins.tolist()
        categories = [
            '{0:.2f} - {1:.2f}'.format(binedges[i], binedges[i + 1])
            for i in range(len(binedges) - 1)
        ]
    else:
        categories = np.unique(hue)
        value_map = {v: i for i, v in enumerate(categories)}
        values = [value_map[d] for d in hue]
    cmap = _norm_cmap(values, cmap, mpl.colors.Normalize, mpl.cm)
    return cmap, categories, values


def _paint_hue_legend(ax, categories, cmap, legend_labels, legend_kwargs, figure=False):
    """
    Creates a discerete categorical legend for ``hue`` and attaches it to the axis.
    """

    # Paint patches.
    patches = []
    for value, _ in enumerate(categories):
        patches.append(
            mpl.lines.Line2D(
                [0], [0], linestyle="none",
                marker="o", markersize=10, markerfacecolor=cmap.to_rgba(value)
            )
        )
    if not legend_kwargs:
        legend_kwargs = dict()

    # If we are given labels use those, if we are not just use the categories.
    target = ax.figure if figure else ax

    if legend_labels:
        target.legend(patches, legend_labels, numpoints=1, fancybox=True, **legend_kwargs)
    else:
        target.legend(patches, categories, numpoints=1, fancybox=True, **legend_kwargs)


def _paint_carto_legend(ax, values, legend_values, legend_labels, scale_func, legend_kwargs):
    """
    Creates a discrete categorical legend for ``scale`` and attaches it to the axis.
    """

    # Set up the legend values and kwargs.
    if legend_values is not None:
        display_values = legend_values
    else:
        display_values = np.linspace(np.max(values), np.min(values), num=5)
    display_labels = legend_labels if (legend_labels is not None) else display_values
    if legend_kwargs is None:
        legend_kwargs = dict()

    # Paint patches.
    patches = []
    for value in display_values:
        patches.append(
            mpl.lines.Line2D(
                [0], [0], linestyle='None',
                marker="o",
                markersize=(20*scale_func(value))**(1/2),
                markerfacecolor='None')
        )
    ax.legend(patches, display_labels, numpoints=1, fancybox=True, **legend_kwargs)


def _paint_colorbar_legend(ax, values, cmap, legend_kwargs):
    """
    Creates a continuous colorbar legend and attaches it to the axis.
    """
    if legend_kwargs is None: legend_kwargs = dict()
    cmap.set_array(values)
    plt.gcf().colorbar(cmap, ax=ax, **legend_kwargs)


def _validate_buckets(hue, scheme):
    """
    This helper method infers if the ``hue`` parameter is categorical, and sets scheme if isn't
    already set.
    """
    categorical = (hue.dtype == np.dtype('object')) if hue is not None else False
    scheme = scheme if scheme else 'Quantiles'
    return categorical, scheme


def _get_clip(extent, clip):
    xmin, xmax, ymin, ymax = extent
    # We have to add a little bit of padding to the edges of the box, as otherwise the edges
    # will invert a little, surprisingly.
    rect = shapely.geometry.Polygon(
        [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)]
    )
    rect = shapely.affinity.scale(rect, xfact=1.25, yfact=1.25)
    for geom in clip:
        rect = rect.symmetric_difference(geom)
    return rect


def _build_voronoi_polygons(df):
    """
    Given a GeoDataFrame of point geometries and pre-computed plot extrema, build Voronoi
    simplexes for the given points in the given space and returns them.

    Voronoi simplexes which are located on the edges of the graph may extend into infinity in some
    direction. In other words, the set of points nearest the given point does not necessarily have
    to be a closed polygon. We force these non-hermetic spaces into polygons using a subroutine.

    Returns a list of shapely.geometry.Polygon objects, each one a Voronoi polygon.
    """
    from scipy.spatial import Voronoi
    geom = np.array(df.geometry.map(lambda p: [p.x, p.y]).tolist())
    vor = Voronoi(geom)

    polygons = []

    for idx_point, _ in enumerate(vor.points):
        idx_point_region = vor.point_region[idx_point]
        idxs_vertices = np.array(vor.regions[idx_point_region])

        is_finite = not np.any(idxs_vertices == -1)

        if is_finite:
            # Easy case, the region is closed. Make a polygon out of the Voronoi ridge points.
            idx_point_region = vor.point_region[idx_point]
            idxs_vertices = np.array(vor.regions[idx_point_region])
            region_vertices = vor.vertices[idxs_vertices]
            region_poly = shapely.geometry.Polygon(region_vertices)

            polygons.append(region_poly)

        else:
            # Hard case, the region is open. Project new edges out to the margins of the plot.
            # See `scipy.spatial.voronoi_plot_2d` for the source of this calculation.
            point_idx_ridges_idx = np.where((vor.ridge_points == idx_point).any(axis=1))[0]

            # TODO: why does this happen?
            if len(point_idx_ridges_idx) == 0:
                continue

            ptp_bound = vor.points.ptp(axis=0)
            center = vor.points.mean(axis=0)

            finite_segments = []
            infinite_segments = []

            pointwise_ridge_points = vor.ridge_points[point_idx_ridges_idx]
            pointwise_ridge_vertices = np.asarray(vor.ridge_vertices)[point_idx_ridges_idx]

            for pointidx, simplex in zip(pointwise_ridge_points, pointwise_ridge_vertices):
                simplex = np.asarray(simplex)

                if np.all(simplex >= 0):
                    finite_segments.append(vor.vertices[simplex])

                else:
                    i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

                    t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
                    t /= np.linalg.norm(t)
                    n = np.array([-t[1], t[0]])  # normal

                    midpoint = vor.points[pointidx].mean(axis=0)
                    direction = np.sign(np.dot(midpoint - center, n)) * n
                    far_point = vor.vertices[i] + direction * ptp_bound.max()

                    infinite_segments.append(np.asarray([vor.vertices[i], far_point]))

            finite_segments = finite_segments if finite_segments else np.zeros(shape=(0,2,2))
            ls = np.vstack([np.asarray(infinite_segments), np.asarray(finite_segments)])

            # We have to trivially sort the line segments into polygonal order. The algorithm that
            # follows is inefficient, being O(n^2), but "good enough" for this use-case.
            ls_sorted = []

            while len(ls_sorted) < len(ls):
                l1 = ls[0] if len(ls_sorted) == 0 else ls_sorted[-1]
                matches = []

                for l2 in [l for l in ls if not (l == l1).all()]:
                    if np.any(l1 == l2):
                        matches.append(l2)
                    elif np.any(l1 == l2[::-1]):
                        l2 = l2[::-1]
                        matches.append(l2)

                if len(ls_sorted) == 0:
                    ls_sorted.append(l1)

                for match in matches:
                    # in list sytax this would be "if match not in ls_sorted"
                    # in numpy things are more complicated...
                    if not any((match == ls_sort).all() for ls_sort in ls_sorted):
                        ls_sorted.append(match)
                        break

            # Build and return the final polygon.
            polyline = np.vstack(ls_sorted)
            geom = shapely.geometry.Polygon(polyline).convex_hull
            polygons.append(geom)

    return polygons


#######################
# COMPATIBILITY SHIMS #
#######################

def _norm_cmap(values, cmap, normalize, cm):
    """
    Normalize and set colormap. Taken from geopandas@0.2.1 codebase, removed in geopandas@0.3.0.
    """
    mn = min(values)
    mx = max(values)
    norm = normalize(vmin=mn, vmax=mx)
    n_cmap = cm.ScalarMappable(norm=norm, cmap=cmap)
    return n_cmap
