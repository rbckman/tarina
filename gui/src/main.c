/*
Copyright (c) 2012, Broadcom Europe Ltd
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

// Test app for VG font library.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>

#include "bcm_host.h"
#include "vgfont.h"

int32_t render_subtitle(GRAPHICS_RESOURCE_HANDLE img, const char *text, const uint32_t text_size, const uint32_t x_offset, const uint32_t y_offset, uint32_t fontcolor)
{
    uint32_t height=0;
    uint32_t img_w, img_h;

    graphics_get_resource_size(img, &img_w, &img_h);

    // split now points to last line of text. split-text = length of initial text. text_length-(split-text) is length of last line
    if (fontcolor == 5) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(225,255,255,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 80, text_size);
        }
    if (fontcolor == 4) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(51,51,51,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 80, text_size);
        }
    if (fontcolor == 3) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(30,30,255,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 80, text_size);
        }
    if (fontcolor == 2) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(255,255,255,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 80, text_size);
        }
    if (fontcolor == 1) {
    graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* fg */
                                     GRAPHICS_RGBA32(200,200,200,0xff), /* bg */
                                     text, 80, text_size);
        }
    return 0;
    }

int main(void)
{
    GRAPHICS_RESOURCE_HANDLE img;
    uint32_t width, height;
    int LAYER=1;
    bcm_host_init();
    int s;

    s = gx_graphics_init(".");
    assert(s == 0);

    s = graphics_get_display_size(0, &width, &height);
    assert(s == 0);

    s = gx_create_window(0, width, height, GRAPHICS_RESOURCE_RGBA32, &img);
    assert(s == 0);

    // transparent before display to avoid screen flash
    graphics_resource_fill(img, 0, 0, width, height, GRAPHICS_RGBA32(0,0,0,0x00));

    graphics_display_resource(img, 0, LAYER, 0, 0, GRAPHICS_RESOURCE_WIDTH, GRAPHICS_RESOURCE_HEIGHT, VC_DISPMAN_ROT0, 1);

    uint32_t text_size = 16;
    FILE * fp;
    FILE * fp2;
    FILE * fp3;
    char * line = NULL;
    //char * b = NULL;
    size_t len;
    ssize_t read;
    int linenr = 0;
    int selected;
    char newread[500];
    char oldread[500];
    char vumeter[130];
    //graphics_resource_fill(img, 0, 0, width, height, GRAPHICS_RGBA32(0,0,0,0xff));
    while (1) {
        // char ch;
        linenr = 0;
        fp = fopen("/dev/shm/interface","r");
        fread(newread, sizeof(char), 500, fp);
        fclose(fp);
        fp3 = fopen("/dev/shm/vumeter","r");
        while(fgets(vumeter, 130, fp3) != NULL);
        fclose(fp3);
        // check if something has changed
        if (strcmp(newread, oldread) != 0) {
            strcpy(oldread, newread);
            //const char *text = "Never give up on your dreams";
            uint32_t y_offset2 = 0;
            uint32_t y_offset3 = 21;
            uint32_t y_offset4 = 42;
            uint32_t y_offset5 = 421;
            uint32_t y_offset6 = 442;
            graphics_resource_fill(img, 0, 0, width, height, GRAPHICS_RGBA32(0,0,0,0xff));
            // blue, at the top (y=40)
            // selected 0 1 2 3 4 5 6 7 8
            int space = 10;
            int morespace = 12;
            int color = 5;
            int row1 = 0;
            int row2 = 0;
            int row3 = 0;
            int row4 = 0;
            int row5 = 0;
            int header = 0;
            // draw the text if updated
            fp2 = fopen("/dev/shm/interface", "r");
            while ((read = getline(&line, &len, fp2)) != -1) {
                //line = b;
                read = read - 1; //don't count the selected line
                line[read] = '\0'; //remove return char
                //printf("%s",line);
                if (linenr == 0)
                    selected = atoi(line);
                if (linenr == selected + 2)
                    color = 1; //selected color
                else
                    color = 5; //unselected
                if ((linenr == 1) && (read > 0))
                    header = 1; //write header menu
                if ((linenr == 1) && (read == 0))
                    header = 0; //write normal menu
                if (header == 0) {
                    if ((linenr == 6) && (read > 0)) //show recording time if there is any
                        render_subtitle(img, line, text_size, 700, y_offset3, 3);
                    if (linenr >= 2 && linenr <= 5){
                        render_subtitle(img, line, text_size, row1, y_offset2, color);
                        row1 += read * space + morespace;
                    }
                    if (linenr >= 7 && linenr <= 10){
                        render_subtitle(img, line, text_size, row2, y_offset3, color);
                        row2 += read * space + morespace;
                    }
                    if (linenr >= 11 && linenr <= 16){
                        render_subtitle(img, line, text_size, row3, y_offset4, color);
                        row3 += read * space + morespace;
                    }
                    if (linenr >= 17 && linenr <= 19){
                        render_subtitle(img, line, text_size, row4, y_offset5, color);
                        row4 += read * space + morespace;
                    }
                    if (linenr >= 20 && linenr <= 32){
                        render_subtitle(img, line, text_size, row5, y_offset6, color);
                        row5 += read * space + morespace;
                    }
                }
                if (header == 1) {
                    if (linenr == 1)
                        render_subtitle(img, line, text_size, 0, y_offset2, 5);
                    if (linenr > 1) {
                        render_subtitle(img, line, text_size, row1, y_offset3, color);
                        row1 += read * space + morespace;
                    }
                }
                linenr += 1;
                free(line);
                line = NULL;
            }
            fclose(fp2);
        //graphics_update_displayed_resource(img, 0, 0, 0, 0);
        }
        uint32_t y_offset = 463;
        render_subtitle(img, vumeter, text_size, 0, y_offset, 5);
        graphics_update_displayed_resource(img, 0, 0, 0, 0);
        usleep(20000);
    }
    graphics_display_resource(img, 0, LAYER, 0, 0, GRAPHICS_RESOURCE_WIDTH, GRAPHICS_RESOURCE_HEIGHT,  VC_DISPMAN_ROT0, 0);
    graphics_delete_resource(img);
    return 0;
}

