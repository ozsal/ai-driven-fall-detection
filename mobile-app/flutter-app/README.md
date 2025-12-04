# Fall Detection System - Mobile App

Flutter mobile application for the Fall Detection System.

## Prerequisites

- Flutter SDK 3.0 or higher
- Android Studio / Xcode
- Firebase project setup

## Installation

1. Install dependencies:
```bash
flutter pub get
```

2. Configure Firebase:
   - Add `google-services.json` (Android) to `android/app/`
   - Add `GoogleService-Info.plist` (iOS) to `ios/Runner/`

3. Update API URL in `lib/services/api_service.dart` or use settings screen

## Running

```bash
flutter run
```

## Features

- Real-time fall event monitoring
- Push notifications for fall alerts
- Event history and details
- Statistics dashboard
- Settings and preferences

## Build

### Android
```bash
flutter build apk
```

### iOS
```bash
flutter build ios
```



