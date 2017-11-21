# LARS' Apple Hunt

## Introduction

Your brand new robot, a LARS (Laboratory for Advanced Systems Research) model JB334, (displayed with a `@`) is on the ground in an field full of apples (displayed with a `O`). The only problem is, your robot doesn't know where to go! Robot's current program drives around randomly, which isn't very good for finding apples, especially since your robot can only take **300** steps before its batteries go dead. 

**You are a programmer for LARS! Your job: write a program to help your robot finds the apples!**

## The Default Program

### Random and the Modulo (Remainder) Operator

Your robot is programmed in Little Python (LP), a variant of the Python programming language. 

The first thing your robot does is generates a random number between 0 and 3 (0, 1, 2 or 3). 

    a = rand % 4

The above code picks one of four numbers using two things -- `rand` and the *modulo* operator `%`. 

The special `rand` variable always returns a random number every time it is read. 

The *modulo* operator can be thought of as "division remainder". So, `4 % 3` is *1*, because `4 / 3` has a remainder of 1. 

If you take a random number from `rand` and apply `% 4` to it, you will end up with a random number between 0 and 3 (try it on a piece of paper to convince yourself!). That random number is saved into the variable `a` using the assignment operation `a = rand % 4`.

### Conditionals: The 'if' Statement

Once your robot has a random number between 0 and 3, it can test that value using the `if` statement and choose to go in one of four directions based on the random number selected.

In an `if` statement, a program asks a question. If the question is **true**, the program executes the code between the curly braces (`{` and `}`). If the question is **false**, nothing happens.

So, the code:

    if x is y {
      z = 3
    }

... will set `z` to 3 *if and only if* the value of `x` equals the value of `y`. **Please note**: the conditional and left bracket (`{`) must be on the first line, followed by the conditional code (here `z = 3`) and finally by the right bracket (`}`) on its own line. 

In addition to `is`, you can test whether something `is not` something else.

Here's the first conditional statement from the default program:


    if a is 0 {
      move = east
    }


This code says "if the variable `a` is equal to *0*, set the variable `move` to *east*." (Remember, `a` was set using `rand` and the modulo (`%`) operator.  

The remaining 3 `if` statements cover west, north and south.

    if a is 1 { 
      move = west 
    } 
    if a is 2 { 
      move = north 
    } 
    if a is 3 { 
      move = south 
    } 

As you may have already guessed, your robot will move in whatever direction the variable `move` is set at the end of your program. Your program will run **300** times, and your score is the number of apples your robot manages to find during that time.

Of course, your current program just walks around randomly. So it's not very good.


## Level 1: Helping Your Robot Find Apples

Your LARS-JB334 robot comes with two apple-detecting sensors. One sensor, `x_dir` tells you whether the closest apple is to the west (left) or the east (right). The other sensor, `y_dir` tells you if the closest apple is to the north (up) or south (down). `x_dir` and `y_dir` equal 0 if you are directly in line with an apple in the given direction.

You can test `x_dir` and `y_dir` using a conditional `if` statement! 

For example:

    if x_dir is east {
         move = east
    }

... checks to see if `x_dir` says that the closest apple is to the east, and if it it is, sets the move to be east.

By creating conditionals that test `x_dir` and `y_dir` for `west`, `north` and `south` (and set `move` accordingly) your robot will walk **directly** towards the closest apple! Try it out for yourself!

**NOTE:** After you change your program, press the `Submit` button.

## Level 2: Avoiding Pits!

Once you clear the first level of apples, things get a little more complicated: Level 2 and above have apples, but they also have **pit traps!** If your LARS-JB334 robot falls into a pit, it breaks and the game ends.

Fortunately, your robot also comes equipped with four pit detectors: `pit_to_north`, `pit_to_south`, `pit_to_east`, and `pit_to_west`. By adding some additional conditional `if` statements (and setting `move` to avoid them), you can make sure that your robot won't step into a pit!
