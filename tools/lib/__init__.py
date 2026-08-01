"""Generation and validation library for the Pathology AI Library.

Design rules (see PLAN.md):
  * data/entries/*.yaml is the single source of truth; everything else is built.
  * Functions return new objects; nothing here mutates its arguments.
  * No network calls in this package — link checking lives in validate.py.
"""
