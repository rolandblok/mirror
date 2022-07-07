float pos = 0;      // pix
float last_update_s;  //s
float delta = 0;
float x = 0;
float y = 0;
float y_ma = 0;
int sin_on = 1;

float noise_scale = 30;
int   ma_depth = 15;


MyMovingAverage ma;


void setup() {
  size(1000, 1000);
  background(255);
  last_update_s = millis() / 1000.0;
  stroke(0);
  translate(0, height/2);
  line (0, 0, width, 0);

  last_update_s = millis()/1000.0;
  loop();

  ma = new MyMovingAverage(ma_depth);
}

float _sign(float x) {
  return ((x) > 0 ? 1 : -1);
}


void draw() {
  translate(0, height/2);

  float cur_time_s =   (millis()/1000.0);
  float d_time_s = cur_time_s - last_update_s;


  last_update_s = cur_time_s;

  //float x = cur_time_s*10;
  float x_new = x + 1;
  float y_new = sin_on*400*sin(x/100) + delta + random(noise_scale);

  ma.add_point(y_new);

  float y_ma_new = ma.get_current();

  stroke(255, 0, 0);
  line(x, y, x_new, y_new);
  x = x_new;
  y = y_new;

  stroke(0, 0, 255);
  line(x, y_ma, x_new, y_ma_new);
  x = x_new;
  y = y_new;
  y_ma = y_ma_new;


  fill(200, 200, 200);
  rect(0, 0 - height / 2, 500, 90);
  fill(0);
  textSize (15);
  text(" y " + y, 10, 15 - height / 2);

  delay (50);
}

void mousePressed() {
  if (mouseButton == RIGHT) {
    delta += 300;
  } else if (mouseButton == LEFT) {
    delta -= 300;
  }
}

void keyPressed() {
  println(key);
  if (key == 'p') {
    noLoop();
  } else if (key == '1') {
    delta += 25;
  } else if (key == '2') {
    delta -= 25;
  } else if (key == 'l') {
    loop();
  } else if (key == 's') {
    sin_on = (sin_on+1)%2;
  } else if (key == 'q') {
    exit();
  }
}

class MyMovingAverage {
  FloatList data;
  int depth;

  float w_top = 50;
  float w_bot = 100;

  MyMovingAverage(int depth) {
    this.data = new FloatList();
    this.depth = depth;
  }
  void add_point(float p) {
    data.append(p);
    if (data.size() > depth) {
      data.remove(0);
    }
  }
  float get_current() {
    float sum = 0;
    float sum_w = 0;
    float last = data.get(data.size()-1);
    for (float d : data) {
      float w = weight(d, last);
      sum += w*d;
      sum_w += w;
    }
    return sum / sum_w;
  }

  float weight(float d_old, float d_new) {
    float delta = abs(d_new - d_old);

    if (delta < w_top) {
      return 1;
    } else if (delta > w_bot) {
      return 0;
    } else {
      return (delta - w_bot) / (w_top-w_bot);
    }
  }
}
