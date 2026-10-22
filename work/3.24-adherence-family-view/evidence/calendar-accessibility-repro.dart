import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:drugtime_mobile/features/adherence/presentation/widgets/adherence_date_picker.dart';

void main() {
  testWidgets('calendar meets Android tap target sizes at 320dp', (tester) async {
    tester.view.physicalSize = const Size(320, 640);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final semantics = tester.ensureSemantics();
    addTearDown(semantics.dispose);
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: Padding(
      padding: const EdgeInsets.all(16),
      child: AdherenceDatePicker(
        selectedDate: DateTime.utc(2026, 10, 22),
        earliestDate: DateTime.utc(2026, 7, 25),
        today: DateTime.utc(2026, 10, 22),
        groups: const [], onSelected: (_) {},
      ),
    ))));
    await tester.pumpAndSettle();
    await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
  });
}
