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

int32_t render_subtitle(GRAPHICS_RESOURCE_HANDLE img, const char *text, const uint32_t text_size, const uint32_t y_offset, uint32_t fontcolor)
{
   uint32_t height=0;
   uint32_t img_w, img_h;

   graphics_get_resource_size(img, &img_w, &img_h);

   // split now points to last line of text. split-text = length of initial text. text_length-(split-text) is length of last line
   if (fontcolor == 5) {
   graphics_resource_render_text_ext(img, 0, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(100,150,150,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 63, text_size);
      }
   if (fontcolor == 4) {
   graphics_resource_render_text_ext(img, 11, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(100,150,150,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 63, text_size);
      }
   if (fontcolor == 3) {
   graphics_resource_render_text_ext(img, 0, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(100,150,150,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 63, text_size);
      }
   if (fontcolor == 2) {
   graphics_resource_render_text_ext(img, 0, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(100,150,150,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 63, text_size);
      }
   if (fontcolor == 1) {
   graphics_resource_render_text_ext(img, 0, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* fg */
                                     GRAPHICS_RGBA32(100,150,150,0xff), /* bg */
                                     text, 63, text_size);
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

   uint32_t text_size = 22;
   char text[63];
   char text2[63];
   char text3[63];
   char text4[63];
   char text5[63];
   char text6[63];
   graphics_resource_fill(img, 0, 0, width, height, GRAPHICS_RGBA32(0,0,0,0xff));
   while (1) {
      // char ch;
      FILE *fp;
      fp = fopen("/dev/shm/vumeter","r");
      while(fgets(text, 63, fp) != NULL);
      fclose(fp);
      FILE *fp2;
      fp2 = fopen("/dev/shm/interface","r");
      fgets(text2, 62, fp2);
      fgets(text3, 62, fp2);
      fgets(text4, 62, fp2);
      fgets(text5, 62, fp2);
      fgets(text6, 62, fp2);
      fclose(fp2);
      //FILE *fp3;
      //fp3 = fopen("interface.txt","r");
      //while(fgets(text3, 57, fp3) != NULL);
      //fclose(fp3);
      //const char *text = "Never give up on your dreams";
      uint32_t y_offset = 460;
      uint32_t y_offset2 = 0;
      uint32_t y_offset3 = 20;
      uint32_t y_offset4 = 40;
      uint32_t y_offset5 = 420;
      uint32_t y_offset6 = 440;
      // graphics_resource_fill(img, 0, 0, width, height, GRAPHICS_RGBA32(0,0,0,0x00));
      // blue, at the top (y=40)

      // draw the text if updated
      render_subtitle(img, text, text_size,  y_offset, 4);
      render_subtitle(img, text2, text_size,  y_offset2, 3);
      render_subtitle(img, text3, text_size,  y_offset3, 5);
      render_subtitle(img, text4, text_size,  y_offset4, 2);
      if(text5[1] == ' ' ) {
      render_subtitle(img, text5, text_size,  y_offset5, 2);
      render_subtitle(img, text6, text_size,  y_offset6, 2);
      }
      if(text5[1] != ' ' ) {
      render_subtitle(img, text5, text_size,  y_offset5, 2);
      render_subtitle(img, text6, text_size,  y_offset6, 1);
      }
      graphics_update_displayed_resource(img, 0, 0, 0, 0);
      usleep(100000);
   }

   graphics_display_resource(img, 0, LAYER, 0, 0, GRAPHICS_RESOURCE_WIDTH, GRAPHICS_RESOURCE_HEIGHT, VC_DISPMAN_ROT0, 0);
   graphics_delete_resource(img);

   return 0;
}

