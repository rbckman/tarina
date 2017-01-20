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
                                     GRAPHICS_RGBA32(100,100,100,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 74, text_size);
      }
   if (fontcolor == 4) {
   graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(51,51,51,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 74, text_size);
      }
   if (fontcolor == 3) {
   graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(60,60,60,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 74, text_size);
      }
   if (fontcolor == 2) {
   graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(255,255,255,0xff), /* fg */
                                     GRAPHICS_RGBA32(0,0,0,0xff), /* bg */
                                     text, 74, text_size);
      }
   if (fontcolor == 1) {
   graphics_resource_render_text_ext(img, x_offset, y_offset-height,
                                     GRAPHICS_RESOURCE_WIDTH,
                                     GRAPHICS_RESOURCE_HEIGHT,
                                     GRAPHICS_RGBA32(255,255,255,0xff), /* fg */
                                     GRAPHICS_RGBA32(20,0,20,0xff), /* bg */
                                     text, 74, text_size);
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

   uint32_t text_size = 20;
   int selected;
   int len_string_header;
   int len_string_film;
   int len_string_scene;
   int len_string_shot;
   int len_string_take;
   int len_string_rec;
   int len_string_shutter;
   int len_string_iso;
   int len_string_red;
   int len_string_blue;
   int len_string_bright;
   int len_string_cont;
   int len_string_sat;
   int len_string_flip;
   int len_string_beep;
   int len_string_lenght;
   int len_string_mic;
   int len_string_phones;
   int len_string_dsk;
   int len_string_more1;
   int len_string_more2;
   int len_string_more3;
   int len_string_more4;
   int len_string_more5;
   int len_string_more6;
   int count = 120;
   char seleold;
   char text[80];
   char text2[4];
   char header[100];
   char film[30];
   char scene[20];
   char shot[20];
   char take[20];
   char rec[20];
   char shutter[30];
   char iso[20];
   char red[20];
   char blue[20];
   char bright[20];
   char cont[20];
   char sat[20];
   char flip[20];
   char beep[20];
   char lenght[20];
   char mic[20];
   char phones[20];
   char dsk[20];
   char more1[20];
   char more2[20];
   char more3[20];
   char more4[20];
   char more5[20];
   char more6[20];
   graphics_resource_fill(img, 0, 0, width, height, GRAPHICS_RGBA32(0,0,0,0xff));
   while (1) {
      // char ch;
      FILE *fp;
      fp = fopen("/dev/shm/vumeter","r");
      while(fgets(text, 74, fp) != NULL);
      fclose(fp);
      FILE *fp2;
      fp2 = fopen("/dev/shm/interface","r");
      fgets(text2, 4, fp2);
      selected = atoi(text2);
      fgets(text2, 4, fp2);
      len_string_header = atoi(text2) + 1;
      fgets(header, len_string_header, fp2);
      fgets(text2, 4, fp2);
      len_string_film = atoi(text2) + 1;
      fgets(film, len_string_film, fp2);
      fgets(text2, 4, fp2);
      len_string_scene = atoi(text2) + 1;
      fgets(scene, len_string_scene, fp2);
      fgets(text2, 4, fp2);
      len_string_shot = atoi(text2) + 1;
      fgets(shot, len_string_shot, fp2);
      fgets(text2, 4, fp2);
      len_string_take = atoi(text2) + 1;
      fgets(take, len_string_take, fp2);
      fgets(text2, 4, fp2);
      len_string_rec = atoi(text2) + 1;
      fgets(rec, len_string_rec, fp2);
      fgets(text2, 4, fp2);
      len_string_shutter = atoi(text2) + 1;
      fgets(shutter, len_string_shutter, fp2);
      fgets(text2, 4, fp2);
      len_string_iso = atoi(text2) + 1;
      fgets(iso, len_string_iso, fp2);
      fgets(text2, 4, fp2);
      len_string_red = atoi(text2) + 1;
      fgets(red, len_string_red, fp2);
      fgets(text2, 4, fp2);
      len_string_blue = atoi(text2) + 1;
      fgets(blue, len_string_blue, fp2);
      fgets(text2, 4, fp2);
      len_string_bright = atoi(text2) + 1;
      fgets(bright, len_string_bright, fp2);
      fgets(text2, 4, fp2);
      len_string_cont = atoi(text2) + 1;
      fgets(cont, len_string_cont, fp2);
      fgets(text2, 4, fp2);
      len_string_sat = atoi(text2) + 1;
      fgets(sat, len_string_sat, fp2);
      fgets(text2, 4, fp2);
      len_string_flip = atoi(text2) + 1;
      fgets(flip, len_string_flip, fp2);
      fgets(text2, 4, fp2);
      len_string_beep = atoi(text2) + 1;
      fgets(beep, len_string_beep, fp2);
      fgets(text2, 4, fp2);
      len_string_lenght = atoi(text2) + 1;
      fgets(lenght, len_string_lenght, fp2);
      fgets(text2, 4, fp2);
      len_string_mic = atoi(text2) + 1;
      fgets(mic, len_string_mic, fp2);     
      fgets(text2, 4, fp2);
      len_string_phones = atoi(text2) + 1;
      fgets(phones, len_string_phones, fp2);
      fgets(text2, 4, fp2);
      len_string_dsk = atoi(text2) + 1;
      fgets(dsk, len_string_dsk, fp2);
      fgets(text2, 4, fp2);
      len_string_more1 = atoi(text2) + 1;
      fgets(more1, len_string_more1, fp2);
      fgets(text2, 4, fp2);
      len_string_more2 = atoi(text2) + 1;
      fgets(more2, len_string_more2, fp2);
      fgets(text2, 4, fp2);
      len_string_more3 = atoi(text2) + 1;
      fgets(more3, len_string_more3, fp2);
      fgets(text2, 4, fp2);
      len_string_more4 = atoi(text2) + 1;
      fgets(more4, len_string_more4, fp2);
      fgets(text2, 4, fp2);
      len_string_more5 = atoi(text2) + 1;
      fgets(more5, len_string_more5, fp2);
      fgets(text2, 4, fp2);
      len_string_more6 = atoi(text2) + 1;
      fgets(more6, len_string_more6, fp2);
      fgets(text2, 3, fp2);
      fclose(fp2);
      if (text2[0] == 'E' && text2[1] == 'O'){
          //FILE *fp3;
          //fp3 = fopen("interface.txt","r");
          //while(fgets(text3, 57, fp3) != NULL);
          //fclose(fp3);
          //const char *text = "Never give up on your dreams";
          uint32_t y_offset = 460;
          uint32_t y_offset2 = 0;
          uint32_t y_offset3 = 22;
          uint32_t y_offset4 = 44;
          uint32_t y_offset5 = 418;
          uint32_t y_offset6 = 440;
          graphics_resource_fill(img, 0, 0, width, height, GRAPHICS_RGBA32(0,0,0,0xff));
          // blue, at the top (y=40)
          // selected 0 1 2 3 4 5 6 7 8
          int space = 10;
          int morespace = 15;
          int color;
          if (seleold != selected){
              count = 0;
              }
          seleold = selected;
          if (count < 200){
          count = count + 1;
          }
          if (count < 100){
          color = 5;
          }
          else{
          color = 4;
          }
          // draw the text if updated
          render_subtitle(img, text, text_size, 0, y_offset, 4);
          if(strlen(header) != 0) {
          render_subtitle(img, header, text_size, 0, y_offset2, 5);
          if(selected == 0){
          render_subtitle(img, film, text_size, 0, y_offset3, 1);
          }
          else{
          render_subtitle(img, film, text_size, 0, y_offset3, color);
          }
          if(selected == 1){
          render_subtitle(img, scene, text_size, len_string_film * space + morespace, y_offset3, 1);
          }
          else{
          render_subtitle(img, scene, text_size, len_string_film * space + morespace, y_offset3, color);
          }
          if(selected == 2){
          render_subtitle(img, shot, text_size, len_string_film * space + len_string_scene * space + morespace * 2, y_offset3, 1);
          }
          else{
          render_subtitle(img, shot, text_size, len_string_film * space + len_string_scene * space + morespace * 2, y_offset3, color);
          }
          if(selected == 3){
          render_subtitle(img, take, text_size, len_string_film * space + len_string_scene * space + len_string_shot * space + morespace * 3, y_offset3, 1);
          }
          else{
          render_subtitle(img, take, text_size, len_string_film * space + len_string_scene * space + len_string_shot * space + morespace * 3, y_offset3, color);
          }
          if(selected == 5){
          render_subtitle(img, shutter, text_size, len_string_film * space + len_string_scene * space + len_string_shot * space + len_string_take * space + morespace * 4, y_offset3, 1);
          }
          else{
          render_subtitle(img, shutter, text_size, len_string_film * space + len_string_scene * space + len_string_shot * space + len_string_take * space + morespace * 4, y_offset3, color);
          }
          if(selected == 6){
          render_subtitle(img, iso, text_size, len_string_film * space + len_string_scene * space + len_string_shot * space + len_string_take * space + len_string_shutter * space + morespace * 5, y_offset3, 1);
          }
          else{
          render_subtitle(img, iso, text_size, len_string_film * space + len_string_scene * space + len_string_shot * space + len_string_take * space + len_string_shutter * space + morespace * 5, y_offset3, color);
          }
          }
          if(strlen(header) == 0) {
          render_subtitle(img, rec, text_size, 700, y_offset5, 2);
          if(selected == 0){
          render_subtitle(img, film, text_size, 0, y_offset2, 1);
          }
          else{
          render_subtitle(img, film, text_size, 0, y_offset2, color);
          }
          if(selected == 1){
          render_subtitle(img, scene, text_size, len_string_film * space + morespace, y_offset2, 1);
          }
          else{
          render_subtitle(img, scene, text_size, len_string_film * space + morespace, y_offset2, color);
          }
          if(selected == 2){
          render_subtitle(img, shot, text_size, len_string_film * space + len_string_scene * space + morespace * 2, y_offset2, 1);
          }
          else{
          render_subtitle(img, shot, text_size, len_string_film * space + len_string_scene * space + morespace * 2, y_offset2, color);
          }
          if(selected == 3){
          render_subtitle(img, take, text_size, len_string_film * space + len_string_scene * space + len_string_shot * space + morespace * 3, y_offset2, 1);
          }
          else{
          render_subtitle(img, take, text_size, len_string_film * space + len_string_scene * space + len_string_shot * space + morespace * 3, y_offset2, color);
          }
          if(selected == 5){
          render_subtitle(img, shutter, text_size, 0, y_offset3, 1);
          }
          else{
          render_subtitle(img, shutter, text_size, 0, y_offset3, color);
          }
          if(selected == 6){
          render_subtitle(img, iso, text_size, (len_string_shutter * space) + morespace, y_offset3, 1);
          }
          else{
          render_subtitle(img, iso, text_size, (len_string_shutter * space) + morespace, y_offset3, color);
          }
          if(selected == 7){
          render_subtitle(img, red, text_size, (len_string_shutter * space) + (len_string_iso * space) + morespace * 2, y_offset3, 1);
          }
          else{
          render_subtitle(img, red, text_size, len_string_shutter * space + len_string_iso * space + morespace * 2, y_offset3, color);
          }
          if(selected == 8){
          render_subtitle(img, blue, text_size, len_string_shutter * space + len_string_iso * space + len_string_red * space + morespace * 3, y_offset3, 1);
          }
          else{
          render_subtitle(img, blue, text_size, len_string_shutter * space + len_string_iso * space + len_string_red * space + morespace * 3, y_offset3, color);
          }
          if(selected == 9){
          render_subtitle(img, bright, text_size, 0, y_offset4, 1);
          }
          else{
          render_subtitle(img, bright, text_size, 0, y_offset4, color);
          }
          if(selected == 10){
          render_subtitle(img, cont, text_size, len_string_bright * space + morespace, y_offset4, 1);
          }
          else{
          render_subtitle(img, cont, text_size, len_string_bright * space + morespace, y_offset4, color);
          }
          if(selected == 11){
          render_subtitle(img, sat, text_size, len_string_bright * space + len_string_cont * space + morespace * 2, y_offset4, 1);
          }
          else{
          render_subtitle(img, sat, text_size, len_string_bright * space + len_string_cont * space + morespace * 2, y_offset4, color);
          }
          if(selected == 12){
          render_subtitle(img, flip, text_size, len_string_bright * space + len_string_cont * space + len_string_sat * space + morespace * 3, y_offset4, 1); 
          }
          else{
          render_subtitle(img, flip, text_size, len_string_bright * space + len_string_cont * space + len_string_sat * space + morespace * 3, y_offset4, color); 
          }
          if(selected == 13){
          render_subtitle(img, beep, text_size, len_string_bright * space + len_string_cont * space + len_string_sat * space + len_string_flip * space + morespace * 4, y_offset4, 1);
          }
          else{
          render_subtitle(img, beep, text_size, len_string_bright * space + len_string_cont * space + len_string_sat * space + len_string_flip * space + morespace * 4, y_offset4, color);
          }
          if(selected == 14){
          render_subtitle(img, lenght, text_size, len_string_bright * space + len_string_cont * space + len_string_sat * space + len_string_flip * space + len_string_beep * space + morespace * 5, y_offset4, 1);
          }
          else{
          render_subtitle(img, lenght, text_size, len_string_bright * space + len_string_cont * space + len_string_sat * space + len_string_flip * space + len_string_beep * space + morespace * 5, y_offset4, color);
          }
          if(selected == 15){
          render_subtitle(img, mic, text_size, 0, y_offset5, 1);
          }
          else{
          render_subtitle(img, mic, text_size, 0, y_offset5, color);
          }
          if(selected == 16){
          render_subtitle(img, phones, text_size, len_string_mic * space + morespace, y_offset5, 1);
          }
          else{
          render_subtitle(img, phones, text_size, len_string_mic * space + morespace, y_offset5, color);
          }
          if(selected == 17){
          render_subtitle(img, dsk, text_size, len_string_mic * space + len_string_phones * space + morespace * 2, y_offset5, 1);
          }
          else{
          render_subtitle(img, dsk, text_size, len_string_mic * space + len_string_phones * space + morespace * 2, y_offset5, color);
          }
          if(selected == 18){
          render_subtitle(img, more1, text_size, 0, y_offset6, 1);
          }
          else{
          render_subtitle(img, more1, text_size, 0, y_offset6, color);
          }
          if(selected == 19){
          render_subtitle(img, more2, text_size, len_string_more1 * space + morespace, y_offset6, 1);
          }
          else{
          render_subtitle(img, more2, text_size, len_string_more1 * space + morespace, y_offset6, color);
          }
          if(selected == 20){
          render_subtitle(img, more3, text_size, len_string_more1 * space + len_string_more2 * space + morespace * 2, y_offset6, 1);
          }
          else{
          render_subtitle(img, more3, text_size, len_string_more1 * space + len_string_more2 * space + morespace * 2, y_offset6, color);
          }
          if(selected == 21){
          render_subtitle(img, more4, text_size, len_string_more1 * space + len_string_more2 * space + len_string_more3 * space + morespace * 3, y_offset6, 1);
          }
          else{
          render_subtitle(img, more4, text_size, len_string_more1 * space + len_string_more2 * space + len_string_more3 * space + morespace * 3, y_offset6, color);
          }
          if(selected == 22){
          render_subtitle(img, more5, text_size, len_string_more1 * space + len_string_more2 * space + len_string_more3 * space + len_string_more4 * space + morespace * 4, y_offset6, 1);
          }
          else{
          render_subtitle(img, more5, text_size, len_string_more1 * space + len_string_more2 * space + len_string_more3 * space + len_string_more4 * space + morespace * 4, y_offset6, color);
          }
          if(selected == 23){
          render_subtitle(img, more6, text_size, len_string_more1 * space + len_string_more2 * space + len_string_more3 * space + len_string_more4 * space + len_string_more5 * space + morespace * 5, y_offset6, 1);
          }
          else{
          render_subtitle(img, more6, text_size, len_string_more1 * space + len_string_more2 * space + len_string_more3 * space + len_string_more4 * space + len_string_more5 * space + morespace * 5, y_offset6, color);      
          }
      }
      graphics_update_displayed_resource(img, 0, 0, 0, 0);
      }
      usleep(100000);
   }

   graphics_display_resource(img, 0, LAYER, 0, 0, GRAPHICS_RESOURCE_WIDTH, GRAPHICS_RESOURCE_HEIGHT, VC_DISPMAN_ROT0, 0);
   graphics_delete_resource(img);
   return 0;
}

