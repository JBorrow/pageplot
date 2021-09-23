Page Plot
=========

One very useful thing to have when developing numerical models is an ability
to rapidly generate a series of diagnostic figures. Usually, you will want
the same number and type of figures each and every time, which usually come
down to a series of scatter plots (with and without binning lines) alongside
some additional data from external sources.

There are a number of ways to do this; you can maintain a set of scripts to
create each plot, or use a dashboard system (like
[Plotly Dash](https://dash.plotly.com/)). Both of these come along with
downsides; for the individual scripts, a lot of time can be spent maintaining
shared code that is frequently copied and pasted between scripts. Those
scripts are essentially just boilerplate, with lots of calls to matplotlib's
API, or a series of pandas calls. Dashboards are tricky in a HPC environment
as they require hosting, and as such are significantly less portable.

PagePlot attempts to slot in-between these solutions. It is a low-code
solution, with the code being used to describe the data format to PagePlot,
with no-code plotting. The figures can then be used to create a static,
portable, dashboard.

PagePlot attempts to succeed the successful
[swift-pipeline](https://github.com/swiftsim/pipeline) project and
generalise it for use throughout the community.


Codeless Plotting
-----------------

A typical diagnostic plot may include a scatter of two variables, along
side a median line to demonstrate the overall trend. Let's take a look at how
that would be done in a typical python script:

```python

import matploylib.pyplot as plt
import numpy as np
import h5py

x_low, x_high = [1e7, 1e10] # cm / s
y_low, y_high = [1e3, 1e9] # km
n_bins = 24

with h5py.File("my_file.hdf5", "r") as handle:
    x_data = handle["/My/X/Data"][:] * 1e5 # km / s to cm / s
    y_data = handle["/My/Y/Data"][:] # km


bins = np.logspace(np.log10(x_low), np.log10(x_high), n_bins)

# ... Your favourite code that does median binning, but produces
bin_centers = ...
medians = ...
scatters = ...

fig, ax = plt.subplots()

ax.set_xscale("log")
ax.set_yscale("log")

ax.scatter(x_data, y_data)

ax.errorbar(bin_centers, medians, scatters)

ax.set_xlim(x_low, x_high)
ax.set_ylim(y_low, y_high)

ax.set_xlabel("X quantity [cm / s]")
ax.set_ylabel("Y quantity [km]")

fig.savefig("test.png")
```

Seems pretty simple, right? All is well when this is one script, dealing with
a fixed data source, with consistent units. The problems originate when you
have changing data (what happens to this script when the simulation software
starts outputting the `x_data` in `cm / s`?), multiple people with different
ideas on how median lines (or other intermediate products) should be created
(should the bin center be placed at the median `x` value or at the midpoint
of the bin edges?), the data should be displayed and visualised
(shaded regions, v.s. error bars, and so-on), all with different packages
used to process the data. This rapidly becomes a big mess (if you're looking
at this package - you've probably been there).

This code doesn't even need to exist. Here, we're just specifying that you would
like a plot of `x` against `y`. I could just as easily have specified this as:

```json
{
    "test": {
        "x": "/My/X/Data",
        "y": "/My/Y/Data",
        "x_units": "cm/s",
        "y_units": "km",
        "median_line": {
            "limits": ["1e7 cm/s", "1e10 cm/s"],
            "bins": 24
        },
        "axes_limits": {
            "limits_x": ["1e7 cm/s", "1e10 cm/s"],
            "limits_y": ["1e3 km", "1e9 km"]
        },
        "scale_axes": {
            "scale_x": "log",
            "scale_y": "log"
        }
    }
}
```

This contains the exact same amount of information (barring the internal data
units from the file, but those should be stored as metadata in the file
anyway). It's much shorter, and is importantly implementation-independent.
I could use this JSON to pass to a `R` script that understands it, or even
write some intermediary to allow `ggplot` to understand it. This JSON
(very convienently) happens to have the exact format used in `PagePlot`.
The library can then control the way that data is processed, and the styling
and output options for the figures in a fully consistent way.



Interfacing With Page Plot
--------------------------