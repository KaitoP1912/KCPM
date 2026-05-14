import 'package:flutter/material.dart';

class AppColors {
  static const Color primary = Color(0xFF24A87A);

  static const Color secondary = Color(0xFF4DA3FF);

  static const Color background = Color(0xFFF5F7FB);

  static const Color surface = Colors.white;

  static const Color textDark = Color(0xFF111827);

  static const Color textLight = Color(0xFF6B7280);

  static const Color border = Color(0xFFE5E7EB);

  static const Color success = Color(0xFF16A34A);

  static const Color danger = Color(0xFFE11D48);

  static const Color warning = Color(0xFFF59E0B);
}

class AppTheme {
  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,

    scaffoldBackgroundColor: AppColors.background,

    fontFamily: 'Inter',

    colorScheme: ColorScheme.light(
      primary: AppColors.primary,
      secondary: AppColors.secondary,
      surface: AppColors.surface,
      error: AppColors.danger,
    ),

    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.background,
      foregroundColor: AppColors.textDark,
      elevation: 0,
      centerTitle: false,
      scrolledUnderElevation: 0,
      titleTextStyle: TextStyle(
        color: AppColors.textDark,
        fontSize: 24,
        fontWeight: FontWeight.w800,
        letterSpacing: -0.5,
      ),
    ),

    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        elevation: 0,
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        minimumSize: const Size(
          double.infinity,
          56,
        ),
        shape: RoundedRectangleBorder(
          borderRadius:
              BorderRadius.circular(20),
        ),
        textStyle: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w800,
          letterSpacing: -0.2,
        ),
      ),
    ),

    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,

      hintStyle: const TextStyle(
        color: AppColors.textLight,
        fontWeight: FontWeight.w500,
      ),

      contentPadding:
          const EdgeInsets.symmetric(
        horizontal: 18,
        vertical: 15,
      ),

      border: OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(18),
        borderSide: const BorderSide(
          color: AppColors.border,
        ),
      ),

      enabledBorder: OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(18),
        borderSide: const BorderSide(
          color: AppColors.border,
        ),
      ),

      focusedBorder: OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(18),
        borderSide: const BorderSide(
          color: AppColors.primary,
          width: 1.4,
        ),
      ),

      errorBorder: OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(18),
        borderSide: const BorderSide(
          color: AppColors.danger,
        ),
      ),

      focusedErrorBorder:
          OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(18),
        borderSide: const BorderSide(
          color: AppColors.danger,
          width: 1.4,
        ),
      ),
    ),

    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor:
            AppColors.primary,
        textStyle: const TextStyle(
          fontWeight: FontWeight.w700,
        ),
      ),
    ),

    cardTheme: CardThemeData(
      color: Colors.white,
      elevation: 0,
      shadowColor: Colors.black
          .withValues(alpha: 0.04),
      shape: RoundedRectangleBorder(
        borderRadius:
            BorderRadius.circular(24),
      ),
    ),

    dividerTheme: const DividerThemeData(
      color: AppColors.border,
      thickness: 1,
      space: 1,
    ),

    bottomNavigationBarTheme:
        const BottomNavigationBarThemeData(
      backgroundColor: Colors.white,
      selectedItemColor:
          AppColors.primary,
      unselectedItemColor:
          AppColors.textLight,
      elevation: 0,
      type: BottomNavigationBarType.fixed,
      selectedLabelStyle: TextStyle(
        fontWeight: FontWeight.w700,
      ),
      unselectedLabelStyle:
          TextStyle(
        fontWeight: FontWeight.w600,
      ),
    ),

    snackBarTheme: SnackBarThemeData(
      backgroundColor:
          AppColors.textDark,
      contentTextStyle:
          const TextStyle(
        color: Colors.white,
        fontWeight: FontWeight.w600,
      ),
      shape: RoundedRectangleBorder(
        borderRadius:
            BorderRadius.circular(18),
      ),
      behavior:
          SnackBarBehavior.floating,
    ),

    progressIndicatorTheme:
        const ProgressIndicatorThemeData(
      color: AppColors.primary,
    ),
  );
}