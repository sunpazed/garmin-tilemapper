using Toybox.WatchUi as Ui;
using Toybox.Graphics as Gfx;
using Toybox.System as Sys;
using Toybox.Lang as Lang;
using Toybox.Application as App;
using Toybox.Timer as Timer;

enum {
  SCREEN_SHAPE_CIRC = 0x000001,
  SCREEN_SHAPE_SEMICIRC = 0x000002,
  SCREEN_SHAPE_RECT = 0x000003
}

class BasicView extends Ui.WatchFace {

    // globals
    var debug = false;
    var is_lowpower = false;
    var deviceSettings = false;

    // time
    var hour = null;
    var minute = null;
    var second = null;

    // layout
    var canvas_h = 0;
    var canvas_w = 0;
    var canvas_shape = 0;
    var canvas_rect = false;
    var canvas_circ = false;
    var canvas_semicirc = false;
    var canvas_tall = false;
    var vert_layout = false;
    var dw = null;
    var dh = null;
    var dw_half = null;
    var dh_half = null;

    // settings
    var set_theme = 1;
    var set_layout = 1;
    var set_leading_zero = false;
    var set_chapter = true;
    var set_date = 0;
    var set_field_1 = 0;
    var set_field_2 = 0;
    var seconds_loaded = false;

    // fonts
    var f_hands = null;
    var current_hand = null;


    function initialize() {
     Ui.WatchFace.initialize();
    }


    function onLayout(dc) {

      // w,h of canvas
      canvas_w = dc.getWidth();
      canvas_h = dc.getHeight();

      // let's grab the canvas shape
      deviceSettings = Sys.getDeviceSettings();
      canvas_shape = deviceSettings.screenShape;

      if (debug) {
        Sys.println(Lang.format("canvas_shape: $1$", [canvas_shape]));
      }

      // find out the type of screen on the device
      canvas_tall = (vert_layout && canvas_shape == SCREEN_SHAPE_RECT) ? true : false;
      canvas_rect = (canvas_shape == SCREEN_SHAPE_RECT && !vert_layout) ? true : false;
      canvas_circ = (canvas_shape == SCREEN_SHAPE_CIRC) ? true : false;
      canvas_semicirc = (canvas_shape == SCREEN_SHAPE_SEMICIRC) ? true : false;

      // set a few constants
      // --------------------------

      // w,h of canvas
      dw = canvas_w;
      dh = canvas_h;

    }


    //! Called when this View is brought to the foreground. Restore
    //! the state of this View and prepare it to be shown. This includes
    //! loading resources into memory.
    function onShow() {
    }


    //! Update the view
    function onUpdate(dc) {


      // grab time objects
      var clockTime = Sys.getClockTime();
      var date = Time.Gregorian.info(Time.now(),0);

      // define time, day, month variables
      hour = clockTime.hour;
      minute = clockTime.min;
      second = clockTime.sec;

      // 12-hour support
      if (hour > 12 || hour == 0) {
          if (!deviceSettings.is24Hour)
              {
              if (hour == 0)
                  {
                  hour = 12;
                  }
              else
                  {
                  hour = hour - 12;
                  }
              }
      }


      // clear the screen
      dc.setColor(0x000000, 0x55dddd);
      dc.clear();

      drawTime(dc,0,0);


    }


    // drawTime()
    // here's where we draw the hands

    function drawTime(targetDc,this_x,this_y) {

      // draw dials
      // --------------------------

      // let's load the dial resources
      f_hands = Ui.loadResource(Rez.Fonts.font_dial);
      current_hand = Ui.loadResource(Rez.JsonData.dialData);

      // draw chapters
      targetDc.setColor(0x000000, Gfx.COLOR_TRANSPARENT);
      drawTiles(current_hand[0],f_hands,targetDc,this_x,this_y);

      // draw face
      targetDc.setColor(0xffffff, Gfx.COLOR_TRANSPARENT);
      drawTiles(current_hand[1],f_hands,targetDc,this_x,this_y);

      // draw tongue and shorts
      targetDc.setColor(0xff0000, Gfx.COLOR_TRANSPARENT);
      drawTiles(current_hand[2],f_hands,targetDc,this_x,this_y);

      // draw shoes
      targetDc.setColor(0xffaa00, Gfx.COLOR_TRANSPARENT);
      drawTiles(current_hand[3],f_hands,targetDc,this_x,this_y);

      // finally, draw the black outline
      targetDc.setColor(0x000000, Gfx.COLOR_TRANSPARENT);
      drawTiles(current_hand[4],f_hands,targetDc,this_x,this_y);


      // draw hour hand
      // --------------------------

      var hour_is = (Math.floor((hour+(minute/60.0))*5.0)).toNumber()%60;
      var hr_is = hour_is;

      // load the appropriate tilemaps as
      // hours are split across four tilemaps;
      // 0_14, 15_29, 30_44, 45_59
      if (hour_is>=45 && hour_is<=59) {
        f_hands = Ui.loadResource(Rez.Fonts.font_hand_45_59);
        current_hand = Ui.loadResource(Rez.JsonData.font_hand_45_59_data);
        hr_is = hour_is - 45;
      }
      if (hour_is>=30 && hour_is<=44) {
        f_hands = Ui.loadResource(Rez.Fonts.font_hand_30_44);
        current_hand = Ui.loadResource(Rez.JsonData.font_hand_30_44_data);
        hr_is = hour_is - 30;
      }
      if (hour_is>=15 && hour_is<=29) {
        f_hands = Ui.loadResource(Rez.Fonts.font_hand_15_29);
        current_hand = Ui.loadResource(Rez.JsonData.font_hand_15_29_data);
        hr_is = hour_is - 15;
      }
      if (hour_is>=0 && hour_is<=14) {
        f_hands = Ui.loadResource(Rez.Fonts.font_hand_0_14);
        current_hand = Ui.loadResource(Rez.JsonData.font_hand_0_14_data);
        hr_is = hour_is;
      }

      // let's draw the actual hour hand tilemap
      targetDc.setColor(0xffffff, Gfx.COLOR_TRANSPARENT);
      drawTiles(current_hand[hr_is+15],f_hands,targetDc,this_x,this_y);
      targetDc.setColor(0x000000, Gfx.COLOR_TRANSPARENT);
      drawTiles(current_hand[hr_is],f_hands,targetDc,this_x,this_y);


      // draw minute hand
      // --------------------------

      var min = minute;

      // load the appropriate tilemaps as
      // minutes are split across four tilemaps;
      // 0_14, 15_29, 30_44, 45_59
      if (minute>=45 && minute<=59) {
        f_hands = Ui.loadResource(Rez.Fonts.font_hand_45_59);
        current_hand = Ui.loadResource(Rez.JsonData.font_hand_45_59_data);
        min = minute - 45;
      }
      if (minute>=30 && minute<=44) {
        f_hands = Ui.loadResource(Rez.Fonts.font_hand_30_44);
        current_hand = Ui.loadResource(Rez.JsonData.font_hand_30_44_data);
        min = minute - 30;
      }
      if (minute>=15 && minute<=29) {
        f_hands = Ui.loadResource(Rez.Fonts.font_hand_15_29);
        current_hand = Ui.loadResource(Rez.JsonData.font_hand_15_29_data);
        min = minute - 15;
      }
      if (minute>=0 && minute<=14) {
        f_hands = Ui.loadResource(Rez.Fonts.font_hand_0_14);
        current_hand = Ui.loadResource(Rez.JsonData.font_hand_0_14_data);
        min = minute;
      }

      // let's draw the actual minute hand tilemap
      targetDc.setColor(0xffffff, Gfx.COLOR_TRANSPARENT);
      drawTiles(current_hand[min+15],f_hands,targetDc,this_x,this_y);
      targetDc.setColor(0x000000, Gfx.COLOR_TRANSPARENT);
      drawTiles(current_hand[min],f_hands,targetDc,this_x,this_y);


    }


    function drawTiles(current_hand,font,dc,xoff,yoff) {

      for(var i = 0; i < current_hand.size(); i++)
      {
        var packed_value = current_hand[i];

        var char = (packed_value&0x00000FFF);
        var xpos = (packed_value&0x003FF000)>>12;
        var ypos = (packed_value&0xFFC00000)>>22;

        dc.drawText(xoff+xpos,yoff+ypos,font,(char.toNumber()).toChar(),Gfx.TEXT_JUSTIFY_LEFT);
      }

    }


    //! Called when this View is removed from the screen. Save the
    //! state of this View here. This includes freeing resources from
    //! memory.
    function onHide() {
    }


    //! The user has just looked at their watch. Timers and animations may be started here.
    function onExitSleep() {

      is_lowpower = false;

    }


    //! Terminate any active timers and prepare for slow updates.
    function onEnterSleep() {

      is_lowpower = true;
      Ui.requestUpdate();

    }


}
