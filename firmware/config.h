#ifndef _CONFIG_H_
#define _CONFIG_H_

#include <avr/io.h>

#define F_CPU       16000000UL
#define F_SYSTICK   1000UL

/* UART definitions, used in uart.c */
#define UART_RX_FIFO_SIZE 64
#define UART_TX_FIFO_SIZE 64
#define UART_BAUDRATE 115200UL

/* Pinout */
#define LED_DDR     DDRB
#define LED_PORT    PORTB
#define LED         5

#define REVERSED
#define WPM_DEFAULT  20

#define KEY_DDR     DDRD
#define KEY_PORT    PORTD
#define KEY_PIN     PIND

#ifndef REVERSED
#define DIT         2
#define DAH         3
#else
#define DAH         2
#define DIT         3
#endif

#define dit_active() (!(KEY_PIN & (1<<DIT)))
#define dah_active() (!(KEY_PIN & (1<<DAH)))


#endif /* _CONFIG_H_ */
