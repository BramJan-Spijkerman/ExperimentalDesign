# Stepper class
class Stepper(step_pin, dir_pin, m0, m1, m2)

Class to control a stepper motor

## Class arguments
- int step_pin      Pin number connected to the step pin of the motor driver
- int dir_pin       Pin number connected to the direction pin of the driver
- int m0            Pin number connected to the first step size pin of the driver
- int m1            Pin number connected to the second step size pin of the driver
- int m2            Pin number connected to the third pin of the driver


## Class methods
- set_step_size(m0_val, m1_val, m2_val)
A method to set the size of the taken motor steps

    - int m0_val        1 / 0 value to toggle the first step size pin
    - int m1_val        1 / 0 value to toggle the second step size pin
    - int m2_val        1 / 0 value to toggle the third step size pin

    - return            void

- set_speed(speed)
A method to set the speed of the motor

    - float speed       Sets the speed by changing the delay between succesife toggles of the step pin

    - return            void


- set_direction(direction)
A method to set the ratation direction of the motor

    - int direction     1 / 0 set the direction of the motor

    - return void


- get_direction()
A method to return the rotation direction of the motor

    - return        int 1 / 0 as the direction


- set_step_pos(step_pos)
A method to manually set the internal step variable i.e. steps taken since initial position

    - int step_pos      number of steps from start position

    - return            void


- step_to(step_position)
A method to move the motor N steps w.r.t. the initial position at startup

    - int step_position     target number of steps

    - return                void



# Stage driver class
class StageDriver(dev_params, step_pin, dir_pin, m0, m1, m2, limit0_pin, limit1_pin)

Class to control the delay stage

## Class arguments
- int step_pin          Pin number connected to the step pin of the motor driver
- int dir_pin           Pin number connected to the direction pin of the driver
- int m0                Pin number connected to the first step size pin of the driver
- int m1                Pin number connected to the second step size pin of the driver
- int m2                Pin number connected to the third pin of the driver
- int limit0_pin        Pin number connected to the limit switch 0
- int limit1_pin        Pin number connected to the limit switch 1


## Class methods
- go_to_zero_pos()
A method to return the stage carriage to the zero position

    -return     void


- set_pos(pos)
A method to manually set the internal position variable of the stage \[mm\]

    - float pos     current position in \[mm\]

    - return        void


- get_pos()
A method to return the value of the internal position variable

    - return        float current position of the stage in \[mm\]


- read_limit_switch(selected_switch)
A method to read the value of the selected limit switch

    - int selected_switch       1 / 0 switch number

    - return                    1 / 0 value of the switch pin


- move_to_pos(target_pos)
A method to move the stage to some target position

    - float target_pos      end position in \[mm\]

    - return                void


# Pico serial handler
class PicoSerialHandler()

...

## Class variables
- ...
- ...
- ...

## Class methods
- ...

- ...

- ...
