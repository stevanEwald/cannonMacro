# to do finish implimenting tooltips
# add hit point tracker
#! /usr/bin/env python3
import customtkinter as ctk
import random
import re
ctk.set_appearance_mode("dark")
root = ctk.CTk()
# ScrollableFrame=ctk.CTkScrollableFrame(root, width =)
root.geometry("1980x1080")
# sets focus on any event that you click on
root.bind_all("<Button-1>", lambda event: event.widget.focus_set())
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
topFrame = ctk.CTkScrollableFrame(root, orientation="horizontal", height=400)
topFrame.grid(row=0, column=0, sticky='new')
frames = []  # list of all frames
widgets = {}  # dictionary of all widget


def rollD(numberOfDice, DiceType):
    rolls = []
    for _ in range(0, int(numberOfDice)):
        rolls.append(random.randint(1, int(DiceType)))
    return rolls


def rollMacro(frame):
    # variable Definitions from Frame class
    rollType = frame.rollType.variable.get()
    attackAmount = int(frame.attackAmount.variable.get())
    attackModifier = int(frame.attackModifier.variable.get())
    armorClass = int(frame.armorClass.variable.get())
    damageDiceAmount = int(frame.damageDiceAmount.variable.get())
    damageDiceType = int(frame.damageDiceType.variable.get()[1:])
    damageModifier = int(frame.damageModifier.variable.get())
    damageThreshold = int(frame.damageThreshold.variable.get())
    rollResults = {}

    rollResults["attackRolls1"] = rollD(attackAmount, 20)
    rollResults["attackRolls2"] = rollD(attackAmount, 20)
    if rollType == "Normal":
        rollResults["attackRollsFinal"] = rollResults["attackRolls1"[:]]
    elif rollType == "Advantage":
        rollResults["attackRollsFinal"] = [
            max(roll1, roll2) for roll1, roll2
            in zip(rollResults["attackRolls1"], rollResults["attackRolls2"])
        ]
    elif rollType == "Disadvantage":
        rollResults["attackRollsFinal"] = [
            min(roll1, roll2) for roll1, roll2
            in zip(rollResults["attackRolls1"], rollResults["attackRolls2"])
        ]
    rollResults["attackRollsModified"] = [
        roll + attackModifier for roll in rollResults["attackRollsFinal"]
    ]
    rollResults.update({
        'hits': [],
        'crits': [],
        'misses': [],
        'critFails': []
        })
    for roll in rollResults["attackRollsFinal"]:
        if roll == 20:
            rollResults['crits'].append(roll)
        elif roll == 1:
            rollResults['critFails'].append(roll)
        elif roll + attackModifier > armorClass:
            rollResults['hits'].append(roll)
        elif roll + attackModifier <= armorClass:
            rollResults['misses'].append(roll)
    rollResults['hitsModified'] = [roll + attackModifier for roll in rollResults["hits"]]
    rollResults["hitDamageRolls"] = [
        rollD(damageDiceAmount, damageDiceType)
        for i in range(0, len(rollResults["hits"]))
        ]
    rollResults["hitDamageSum"] = [
        sum(sublist) for sublist in rollResults["hitDamageRolls"]
        ]
    rollResults["hitDamageModified"] = [
        damage + damageModifier for damage in rollResults["hitDamageSum"]
        ]
    rollResults["hitDamageThreshold"] = [
        0 if damage < damageThreshold
        else damage for damage in rollResults["hitDamageModified"]
        ]
    rollResults["hitDamageTotal"] = sum(rollResults["hitDamageThreshold"])
    rollResults["critDamageRolls"] = [
        rollD(damageDiceAmount, damageDiceType)
        for i in range(0, len(rollResults["crits"]))
        ]
    rollResults["critDamageSum"] = [
        sum(sublist) for sublist in rollResults["critDamageRolls"]
        ]
    return rollResults


def calculate():
    global frameRollResults
    frameRollResults = {}
    totalDamage = []
    for frame in frames:
        RollResults = rollMacro(frame)
        frameRollResults.update(RollResults)
        hitCountsValues = [
            f"Hits: {len(RollResults['hits'])}",
            f"Crits: {len(RollResults['crits'])}",
            f"Misses: {len(RollResults['misses'])}",
            f"Crit Fails: {len(RollResults['critFails'])}"
        ]
        # hitCountsToolTipValues = [
        #     RollResults['hits'],
        #     RollResults['crits'],
        #     RollResults['misses'],
        #     RollResults['critFails']
        #     ]
        # hitDamageValues = [
        #     f"Hit Damage:{RollResults['hitDamageTotal']}",
        #     f"Crit Damage:{RollResults['critDamageSum']}",
        # ]

        # hitCountToolTipValues = [
        #     RollResults['hits'],
        #     RollResults['crits'],
        #     RollResults['misses'],
        #     RollResults['critFails'],
        # ]
        frame.hitCounts.type.configure(values=hitCountsValues)
        frame.attackRolls.type.configure(
            text=f"Hit Attack Rolls:{str(RollResults['hitsModified']).strip('[]')}")
        frame.hitDamageRolls.type.configure(
            text=f"Hit Damage Rolls:{str(RollResults['hitDamageSum']).strip('[]')}")
        frame.hitDamageTotal.type.configure(
            text=f"Hit Damage Total:{str(RollResults['hitDamageTotal']).strip('[]')}")
        frame.critDamageRolls.type.configure(
            text=f"Crit Damage Rolls:{str(RollResults['critDamageSum']).strip('[]')}")
        totalDamage.append(RollResults['hitDamageTotal'])
        # frame.hitCounts.refreshSegments(hitCountsValues,
        #                                 hitCountsToolTipValues)
        # frame.hitDamageAmount.refreshSegments(RollResults['hitDamageSum'])
        # frame.hitDamageAmount.refreshSegments(RollResults['critDamageSum'])
        # frame.hitDamage.toolTipValues = hitDamageValues
        # frame.hitCounts.type.configure(toolTipValues=hitCountToolTipValues)
        # frame.hitDamage.type.configure(values=frameRollResults["hitDamageSum"])
    bottomFrame.totalDamage.type.configure(text=f"Total Damage:{sum(totalDamage)}")
    return frameRollResults,


def addFrame(n):
    """_summary_
    Adds a new frame populated with widgets when the add frame button is pushed

    Args:
        n (_type_): _description_ frame number
    """
    for _ in range(0, n):
        Frame(f"Frame{len(frames) + 1}", topFrame, border_width=1)


def subtractFrame():
    """_summary_
    deletes the frame farthest to the right
    """
    frameToRemove = frames[-1]
    for widget in frameToRemove.frame.winfo_children():
        widget.destroy()
    frameToRemove.frame.destroy()
    frames.pop()


class Widget:
    def __init__(
        self,
        name,
        master,
        type,
        default,
        labelText,
        row,
        column,
        sticky,
        **kwargs
    ):
        self.name = name
        self.master = master  # master window
        self.type = type  # type of widget
        self.default = default  # default text/option
        self.widgetName = f"{self.name}{type}"
        self.label = f"{self.name}label"  # label widget name
        self.labelText = labelText  # Label Text
        self.variable = f"{self.name}Var"  # variable
        if self.type == "menu" or self.type == 'segmentedButton':
            self.variable = ctk.StringVar(master)
        else:
            self.variable = ctk.IntVar(master)
        self.variable.set(default)
        self.row = row
        self.column = column
        self.sticky = sticky
        # kwargs definitons
        self.labelPadx = kwargs.pop("labelPadx", 5)
        self.labelPady = kwargs.pop("labelPady", 0)
        self.labelFont = kwargs.pop("labelFont", ("Arial Unicode MS", 15))
        self.labelColor = kwargs.pop("labelColor", "gray14")
        self.labelColumnSpan = kwargs.pop("labelColumnSpan", 1)
        self.labelWidth = kwargs.pop('labelWidth', 30)
        self.limit = kwargs.pop("limit", 2)
        self.width = kwargs.pop("width", 130)
        self.padx = kwargs.pop("padx", 5)
        self.pady = kwargs.pop("pady", 3)
        self.columnspan = kwargs.pop("columnspan", 3)
        self.font = kwargs.pop("font", ("Arial Unicode MS", 15))
        self.anchor = kwargs.pop("anchor", "w")
        self.anchorMenu = kwargs.pop("anchormenu", "center")
        self.justify = kwargs.pop("justify", "center")
        self.borderWidth = kwargs.pop("border_width", 0)
        self.buttonValues = kwargs.pop("buttonValues", [])
        self.toolTipValues = kwargs.pop("toolTipValues", [])
        self.tooltip = None
        self.segments = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

        if labelText:
            self.label = ctk.CTkLabel(
                master,
                font=self.labelFont,
                text=labelText,
                fg_color=self.labelColor,
                width=self.labelWidth,
            )
            self.label.grid(
                row=row,
                column=column,
                padx=self.labelPadx,
                pady=self.labelPady,
                columnspan=self.labelColumnSpan,
                sticky="w",
            )
        if type == "entry":
            def entryValidate(newval):
                return re.match("^[0-9]*$", newval)\
                    is not None and len(newval) <= self.limit
            entryValidateWrapper = (root.register(entryValidate), "%P")
            self.type = ctk.CTkEntry(
                master,
                textvariable=self.variable,
                font=self.font,
                justify=self.justify,
                border_width=self.borderWidth,
                width=self.width,
                validate='key',
                validatecommand=entryValidateWrapper,
                **kwargs,
            )
            self.type.grid(
                row=row,
                column=column + 1,
                padx=self.padx,
                pady=self.pady,
                columnspan=self.columnspan,
                sticky=self.sticky,
            )
        elif type == "menu":
            self.type = ctk.CTkOptionMenu(
                master,
                variable=self.variable,
                anchor=self.anchorMenu,
                font=self.font,
                width=self.width,
                **kwargs,
            )
            self.type.grid(
                row=row,
                column=column + 1,
                padx=self.padx,
                pady=self.pady,
                columnspan=self.columnspan,
                sticky=self.sticky,
            )
        elif type == "button":
            self.type = ctk.CTkButton(
                master,
                text=default,
                font=self.font,
                **kwargs
            )
            self.type.grid(
                row=row,
                column=column + 1,
                padx=self.padx,
                pady=self.pady,
                columnspan=self.columnspan,
                sticky=self.sticky,
            )
        elif type == "segmentedButton":
            self.type = ctk.CTkSegmentedButton(
                master,
                font=self.font,
                width=self.width,
                **kwargs
            )
            self.type.grid(
                row=row,
                column=column + 1,
                padx=self.padx,
                pady=self.pady,
                columnspan=self.columnspan,
                sticky=self.sticky,
            )
        elif type == "segmentedButtonToolTip":
            self.type = ctk.CTkFrame(
                master,
                fg_color='gray14',
                width=self.width
            )
            self.type.grid(
                row=row,
                column=column + 1,
                padx=self.padx,
                pady=self.pady,
                columnspan=self.columnspan,
                sticky=self.sticky,
            )
        if type == "label":
            self.type = ctk.CTkLabel(
                master,
                font=self.font,
                text=self.default,
                width=self.width,
                **kwargs
            )
            self.type.grid(
                row=row,
                column=column + 1,
                padx=self.padx,
                pady=self.pady,
                columnspan=self.columnspan,
                sticky=self.sticky,
            )

        self.refreshSegments(self.buttonValues, self.toolTipValues)

    def refreshSegments(self, buttonValues, toolTipValues, **kwargs):
        # deletes all segments and clears dictionary
        for segment in self.segments:
            self.segments[segment].destroy()
        self.segments.clear()

        for value in buttonValues:
            segmentName = f'segment{buttonValues.index(value)+1}'
            segment = ctk.CTkButton(
                self.type,
                width=self.width/len(buttonValues),
                font=self.font,
                text=buttonValues[buttonValues.index(value)],
                fg_color=('gray14'),
                **kwargs
            )
            self.segments.update({segmentName: segment})
            segment.grid(
                row=0,
                column=buttonValues.index(value),
                sticky='nw'
            )
            segment.bind(
                "<Enter>",
                lambda event, name=segmentName:
                self.show_tooltip(
                    self.segments.get(name),
                    toolTipValues[buttonValues.index(value)]
                )
            )

    def show_tooltip(self, segment, toolTipValue):
        if self.tooltip:
            self.hide_tooltip()
        x, y, _, _ = segment.bbox("insert")  # Get coordinates of segment
        x = self.type.winfo_rootx()-30
        y = self.type.winfo_rooty()
        self.tooltip = ctk.CTkToplevel(self.master)
        self.tooltip.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip.wm_geometry(f"+{x+30}+{y+27}")  # place tooltip
        textBox = ctk.CTkTextbox(
            self.tooltip,
            width=self.width,
            wrap='word',
            height=100,
            border_width=2,
            corner_radius=5
        )
        segment.bind("<Leave>", self.hide_tooltip)
        self.tooltip.bind("<Leave>", self.hide_tooltip)
        self.master.bind("<Leave>", self.hide_tooltip)
        topFrame.bind("<Leave>", self.hide_tooltip)
        root.bind("<Leave>", self.hide_tooltip)

        # label.bind("<Configure>", label.adjust_height)
        # def adjust_height(label, event):
        #     label.configure(height=int(label.index('end-1c').split('.')[0]))
        textBox.insert("1.0", text=f'{toolTipValue}')
        textBox.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

        widgets.update({self.name: self})


class Frame:
    def __init__(self, name, master, **kwargs):
        self.master = master
        self.name = name
        self.frame = ctk.CTkFrame(master, fg_color="gray14", **kwargs)
        self.frame.grid(row=0, column=len(frames))
        # top Frame Widgets
        # Widget Key (master, type, default,
        # labelText, row, column, sticky, **kwargs
        self.rollType = Widget(
            "rollType", self.frame, "menu", "Normal", "Roll Type:",
            0, 0, "ew",
            values=("Normal", "Advantage", "Disadvantage"),
        )
        self.attackModifier = Widget(
            "attackModifier", self.frame, "entry", "0", "Attack Modifier:",
            1, 0, "ew",
        )
        self.attackAmount = Widget(
            "attackAmount", self.frame, "entry", "1", "Number of Attacks:",
            2, 0, "ew",
        )
        self.damageDiceAmount = Widget(
            "damageDiceAmount", self.frame, "entry", "1", "Damage Dice:",
            3, 0, "e",
            width=50,
            padx=(5, 0),
            justify="center",
            columnspan=1,
            limit=2,
        )
        self.damageDiceType = Widget(
            "damageDiceType", self.frame, "menu", "D10", "",
            3, 1, "ew",
            values=["D4", "D6", "D8", "D10", "D12", "D20"],
            width=50,
            fg_color=("#F9F9FA", "#343638"),
            button_color=("#F9F9FA", "#343638"),
            button_hover_color=("#F9F9FA", "#343638"),
            padx=0,
            columnspan=1,
        )
        self.damageDiceLabelCover = Widget(
            "damageDiceLabelCover", self.frame, "label", "", "",
            3, 0, "w",
            width=10,
            padx=(50, 0),
            columnspan=2,
            fg_color=("#F9F9FA", "#343638")
            )
        self.damageDiceLabelCover.type.lift()  # lifts label above others
        self.damageModifier = Widget(
            'damageModifier', self.frame, "entry", "0", "+",
            3, 2, "w",
            width=50,
            columnspan=1,
            padx=(0, 5),
            limit=3,
            labelColor=("#F9F9FA", "#343638"),
            labelFont=("Arial Unicode MS", 20),
            labelPadx=(40, 0),
            labelWidth=(40),
            labelColumnSpan=2
        )
        self.damageModifier.label.lift()  # lifts + label above others
        self.armorClass = Widget(
            "armorClass", self.frame, "entry", "10", "Armor Class:",
            4, 0, "ew"
        )
        self.damageThreshold = Widget(
            "damageThreshold", self.frame, "entry", "0", "Damage Threshold:",
            5, 0, "ew",
        )
        self.hitCounts = Widget(
            "hitCounts", self.frame, "segmentedButton", "", "",
            7, -1, "ew",
            state="disabled",
            fg_color=('gray14'),
            columnspan=4,
            text_color_disabled="white",
            values=["Hits:", "Crits:", "Misses:", "Crit Fails:"],
            width=200,
            anchor='w'
        )
        self.attackRolls = Widget(
            "attackRolls", self.frame, "label", "", "",
            8, -1, "w",
            fg_color=('gray14'),
            columnspan=4,
            padx=5,
            width=30,
        )
        self.hitDamageRolls = Widget(
            "hitCounts", self.frame, "label", "", "",
            9, -1, "w",
            fg_color=('gray14'),
            columnspan=4,
            padx=5,
            width=30,
            anchor='w'
        )
        self.hitDamageTotal = Widget(
            "hitDamageTotal", self.frame, "label", "", "",
            10, -1, "w",
            fg_color=('gray14'),
            columnspan=4,
            padx=5,
            width=30,
        )
        self.critDamageRolls = Widget(
            "critDamageRolls", self.frame, "label", "", "",
            11, -1, "w",
            fg_color=('gray14'),
            columnspan=4,
            padx=5,
            width=30,
            anchor='w'
        )
        # self.hitCounts = Widget(
        #     "hitCounts", self.frame, "segmentedButtonToolTip", "", "",
        #     8, -1, "ew",
        #     state="disabled",
        #     fg_color=('gray14'),
        #     columnspan=4,
        #     text_color_disabled="white",
        #     buttonValues=["Hits:", "Crits:", "Misses:", "Crit Fails:"],
        #     toolTipValues=[],
        #     width=200,
        # )
        # self.hitDamageAmount = Widget(
        #     "hitDamageAmount", self.frame, "segmentedButton", "", "",
        #     8, -1, "ew",
        #     state="disabled",
        #     fg_color=('gray14'),
        #     columnspan=4,
        #     text_color_disabled="white",
        #     buttonValues=[""],
        #     width=200,
        # )
        # self.critDamageAmount = Widget(
        #     "critDamageAmount", self.frame, "segmentedButton", "", "",
        #     8, -1, "ew",
        #     state="disabled",
        #     fg_color=('gray14'),
        #     columnspan=4,
        #     text_color_disabled="white",
        #     buttonValues=[""],
        #     width=200,
        # )

        # self.hitDamage = Widget(
        #     "hitDamage", self.frame, "segmentedButtonToolTip", "","",
        # 9, -1, "ew",
        #     state = "disabled",
        #     fg_color=('gray14'),
        #     columnspan= 4,
        #     text_color_disabled = "white",
        #     values = ['Hit Damage:', 'Crit Damage:'],
        #     width = 200,
        # )
        frames.append(self)


class BottomFrame:
    def __init__(self, master):
        self.__name__ = "Bottom Frame"
        self.frame = ctk.CTkFrame(master, fg_color='gray14',)
        self.frame.grid(row=1, column=0, sticky='nw')

        self.roll = Widget(
            "roll", self.frame, "button", "Roll", "",
            1, -1, "ew",
            command=calculate,
            columnspan=4,
        )
        self.addFrame = Widget(
            "addFrame", self.frame, "button", "+", "",
            0, -1, "ew",
            width=10,
            columnspan=1,
            command=lambda: addFrame(1),
        )
        self.subtractFrame = Widget(
            "subtractFrame", self.frame, "button", "-", "",
            0, 0, "ew",
            command=subtractFrame,
            width=10,
            columnspan=1,
        )
        self.totalDamage = Widget(
            "Total Damage:", self.frame, "label", "", "",
            2, -1, "ew",
            fg_color=('gray14'),
            columnspan=4,
            width=200,
        )


bottomFrame = BottomFrame(root)
addFrame(2)
frames[0].attackAmount.variable.set("6")
frames[0].damageDiceAmount.variable.set("8")
frames[1].attackAmount.variable.set("9")
frames[1].damageDiceAmount.variable.set("6")
root.mainloop()
