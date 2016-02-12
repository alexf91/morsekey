#include "config.h"
#include <util/delay.h>
#include <avr/interrupt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "uart.h"
#include "system.h"

#define BUFSIZE 32

enum states {
    STATE_IDLE,
    STATE_SPACE_WAIT,
    STATE_DIT,
    STATE_DIT_WAIT,
    STATE_DAH,
    STATE_DAH_WAIT
};

void delay_ms(uint16_t d) {
    while(d) {
        _delay_us(980);
        d--;
    }
}

int main(void) {
    uint8_t state = STATE_IDLE;
    uint8_t wpm = WPM_DEFAULT;
    uint16_t dit_time = 1200 / wpm;

    KEY_DDR  &= ~((1<<DIT) | (1<<DAH));
    KEY_PORT |= (1<<DIT) | (1<<DAH);

    uart_init();

    sei();
    while(1) {
        if(state ==  STATE_IDLE) {
            if(dit_active())
                state = STATE_DIT;
            else if(dah_active())
                state = STATE_DAH;
        }
        else if(state == STATE_SPACE_WAIT) {
            uint8_t breaked = 0;
            for(uint8_t i=0; i<dit_time; i++) {
                if(dit_active()) {
                    state = STATE_DIT;
                    breaked = 1;
                    break;
                }
                else if(dah_active()) {
                    state = STATE_DAH;
                    breaked = 1;
                    break;
                }
                delay_ms(1);
            }
            if(!breaked) {
                state = STATE_IDLE;
                uart_puts("\n");
            }
        }
        else if(state == STATE_DIT) {
            uart_puts(".");
            delay_ms(dit_time);
            state = STATE_DIT_WAIT;
        }
        else if(state == STATE_DIT_WAIT) {
            delay_ms(dit_time);
            if(dah_active())
                state = STATE_DAH;
            else if(dit_active())
                state = STATE_DIT;
            else
                state = STATE_SPACE_WAIT;
        }
        else if(state == STATE_DAH) {
            uart_puts("-");
            delay_ms(3*dit_time);
            state = STATE_DAH_WAIT;
        }
        else if(state == STATE_DAH_WAIT) {
            delay_ms(dit_time);
            if(dit_active())
                state = STATE_DIT;
            else if(dah_active())
                state = STATE_DAH;
            else
                state = STATE_SPACE_WAIT;
        }
    }
    
    uint8_t read = uart_read_noblock(&wpm, 1);
    if(read && wpm)
        dit_time = 1200 / wpm;
}
