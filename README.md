# wealth-distribution-rock-paper-scissors

Wealth distribution scenarios based on rock-paper-scissors game.

*TODO: Explain what this is about, how to use it and add screencasts. Explore the implications.*

## Running

Prepare the Python virtual environment:

```sh
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Run the application:

```sh
python wealth-distribution-rock-paper-scissors.py
```

You can tweak the configuration in `wealth-distribution-rock-paper-scissors.py` before running the application:
```py
class CONF:
    initial_wealth = 5  # should be >= 1; smaller numbers give more dramatic results
    debt_treshold = 0  # should be <= 0; or None for unlimited debt
    gini_revolution_treshold = 0.7  # should be > 0 and < 1; None for no revolution
```

## References

1. Ugo Bardi. [The Seneca Effect: Why Growth is Slow but Collapse is Rapid](https://www.springer.com/gp/book/9783319572062)
1. Mark Sponsler. [What is a storm?](http://www.stormsurf.com/page2/tutorials/weatherbasics.shtml)
1. Buck Shlegeris. [Gini coefficient calculator](http://shlegeris.com/gini)
1. Walter Scheidel. [The Great Leveler: Violence and the History of Inequality from the Stone Age to the Twenty-First Century](https://press.princeton.edu/books/paperback/9780691183251/the-great-leveler)
1. Robert MacCulloch. [Income Inequality and the Taste for Revolution](https://www.journals.uchicago.edu/doi/abs/10.1086/426881?journalCode=jle)
1. Kohler, T., Smith, M., Bogaard, A. et al. [Greater post-Neolithic wealth disparities in Eurasia than in North America and Mesoamerica](https://www.nature.com/articles/nature24646) (and [a summarizing article](https://www.inverse.com/article/38457-inequality-study-nature-revolution))
1. Max Roser and Esteban Ortiz-Ospina. [Income Inequality](https://ourworldindata.org/income-inequality)
1. Lane Kenworthy and Timothy Smeeding. [Growing inequalities and their impacts in the United States](http://gini-research.org/system/uploads/443/original/US.pdf?1370077377)
1. [Google search for Gini index](https://www.google.com/search?q=gini+index+revolution)

