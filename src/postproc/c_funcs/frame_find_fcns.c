/*****************************************************************************
This is the C code that has helper functions that help the daq_comms perform
frame-finding in a fast and efficient manner
*****************************************************************************/


#include<stdio.h>
#include<stdlib.h>
#include<stdbool.h>
#include<math.h>


enum state_var {
    RESET, WAITING_FOR_TURN, TURNING_MIN, TURNING_MAX, 
    RUNNING_TO_MIN, RUNNING_TO_MAX
}


enum dir_var {
    FORWARD, REVERSE, UNKNOWN
}

/*
To determine which direction things are going we have to either have a history
of a few samples, or we have to go into the future by a few samples.  
An important point - by "samples" here I mean changes in az_vals.  Since in 
this application there are almost always several of the same az val in a row,
we have to wait for a few "transitions" before we can safely determine azimuth 
motor movement direction


*/

/*
Function Name: get_frame_limit_inds()
Description:
    

Arguments:
    (double*) az_vals_in 
        a 1D array of azimuth encoder values to be scanned for finding the 
        turnaround

    (int) len_az
        length of "az_vals_in"

*/
int get_frame_limit_inds(double *az_vals_in, int len_az, double min_az, 
        double max_az, int *frame_starts_out, int *frame_ends_out) {
       

    // state variable
    state_var state = RESET;

    // direction of the motor movement
    dir_var direction = UNKNOWN;

    // indices marking our place in the frame start and end output arrays
    int starts_out_ind = 0;
    int ends_out_ind = 0;

    // number of transitions before direction can be determined 
    const int TRANS_MIN = -3;
    const int TRANS_MAX = 3;
    int trans_cntr = 0;

    double prev_az = az_vals_in[0];
    double curr_az = az_vals_in[0];

    // main "for" loop
    for (int i=0; i<len_az; i++) {
        curr_az = az_vals_in[i];
        
        // checking this first saves the most time as it happens about
        // 98.75% of the time or more 
        if (curr_az == prev_az) {
            continue;
        }

        if (direction == UNKNOWN) {

        // transition has occurred
        if (curr_az < prev_az) {
            if (trans_cntr > TRANS_MIN) {
                trans_cntr -= 1;
            }
        } else {
            if (trans_cntr < TRANS_MAX) {
                trans_cntr += 1;
            }
        }

        // update direction if you can
        if (direction == UNKNOWN) {
            if (trans_cntr >= TRANS_MAX) {
                direction = FORWARD;
            } else if (trans_cntr <= TRANS_MIN) {
                direction = REVERSE;
            }
        }

        

        if (direction == UNKNOWN) { 

        }

    
    }

    return 0;
}
