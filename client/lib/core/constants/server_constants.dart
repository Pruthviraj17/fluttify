import 'dart:io';

class ServerConstants {
  static String serverUrl =
      Platform.isAndroid ? 'http://10.0.2.2:8000' : 'http://127.0.0.1:8000';

  // when running on physical ios device use this
  // static String serverUrl =
  //     Platform.isAndroid ? 'http://10.0.2.2:8000' : 'http://192.168.1.2:8000';
}
