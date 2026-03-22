# DND dice roller
Dnd dice roller is an automatic dice roller that makes dice rolling super quick for those who want a fast way rolling dice in dnd and who may struggle with calculating everything in your head.

Why is this better and worse than other online dice rollers?
* It is faster but takes longer to set up. (That it.)

# How to setup
in the config.json you can change settings and dice setups.
This app requires customtkiner and dataclasses
# Keybinds
## Tabs
'1-9' and '0' will change tabs/categories.
After you have selected 
## Dice selection
You simply type out the dice throw you want. Only in english alphabet
## Live custom dice
pressing '.' will begin the custom dice roll where you can roll dice(es) on the fly without creating one in the config.
The way you chosse the dice is by pressing out something like ``.10b2d10``. < this one will create a 2d10 dice roll with a bonus of 10.
### Live custom dice examples:
* ``.d10`` will create a 1d10 dice roll.
* ``.5bd7`` will create a 1d7 dice roll with a bonus of 5.
* ``.`` will create a 1d4 dice roll. (Default if you put nothing)

# Config
```
{
  "your tab/category name":
  [
    {
      name: "Dice throw name here",
      bonus: bonus as a number,
      dice: a list with 2 values. [amount of dice rolled, dice number]
    },
    ...,
    ...
  ]

  settings:
  {
    binds:
    [
      "\*your tab/category name\*",
      ...,
      ...
    ],
    animation: "animation name" (QUICK, FADE_IN and RANDOM_NUMBERS),
    animationSpeed: "animation speed"
  }
}
```
