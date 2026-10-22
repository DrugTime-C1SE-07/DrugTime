import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:drugtime_mobile/features/adherence/domain/entities/adherence_history.dart';
import 'package:drugtime_mobile/features/adherence/domain/repositories/adherence_repository.dart';
import 'package:drugtime_mobile/features/adherence/presentation/state/adherence_controller.dart';
import 'package:drugtime_mobile/features/adherence/presentation/widgets/adherence_date_picker.dart';

class EmptyRepository implements AdherenceRepository {
  final ranges = <(DateTime, DateTime)>[];
  @override
  Future<AdherenceHistory> fetch({required String patientId, required DateTime from, required DateTime to}) async {
    ranges.add((from, to));
    return AdherenceHistory(patientId: patientId, from: from, to: to, asOf: DateTime.utc(2026, 10, 22),
      summary: const AdherenceSummary(total: 0, taken: 0, late: 0, missed: 0, pending: 0, counted: 0, rate: null), groups: const []);
  }
}

void main() {
  test('all four 90-day boundaries produce bounded queries', () async {
    final repo = EmptyRepository();
    final controller = AdherenceController(repo, patientId: '11111111-1111-4111-8111-111111111111', now: () => DateTime.utc(2026, 10, 22, 5));
    try {
      expect(await controller.selectDate(DateTime.utc(2026, 7, 24)), isFalse);
      expect(await controller.selectDate(DateTime.utc(2026, 7, 25)), isTrue);
      expect(repo.ranges.single, (DateTime.utc(2026, 7, 25), DateTime.utc(2026, 7, 31)));
      expect(await controller.selectDate(DateTime.utc(2026, 10, 22)), isTrue);
      expect(repo.ranges.last, (DateTime.utc(2026, 10, 1), DateTime.utc(2026, 10, 22)));
      expect(await controller.selectDate(DateTime.utc(2026, 10, 23)), isFalse);
      expect(repo.ranges.length, 2);
      for (final (from, to) in repo.ranges) {
        expect(to.difference(from).inDays + 1, lessThanOrEqualTo(90));
      }
    } finally { controller.dispose(); }
  });

  testWidgets('month navigation locks old and future dates at both ends', (tester) async {
    DateTime? selected;
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: AdherenceDatePicker(
      selectedDate: DateTime.utc(2026, 10, 22), earliestDate: DateTime.utc(2026, 7, 25), today: DateTime.utc(2026, 10, 22),
      groups: const [], onSelected: (date) => selected = date,
    ))));
    Future<void> tap(Finder finder) async { await tester.ensureVisible(finder); await tester.tap(finder); await tester.pumpAndSettle(); }
    await tap(find.byKey(const Key('adherence-calendar-toggle')));
    expect(tester.widget<IconButton>(find.byWidgetPredicate((w) => w is IconButton && w.tooltip == 'Tháng sau')).onPressed, isNull);
    await tap(find.text('23'));
    expect(selected, isNull);
    for (var i = 0; i < 3; i++) { await tap(find.byTooltip('Tháng trước')); }
    expect(find.text('Tháng 7, 2026'), findsOneWidget);
    expect(tester.widget<IconButton>(find.byWidgetPredicate((w) => w is IconButton && w.tooltip == 'Tháng trước')).onPressed, isNull);
    await tap(find.text('24'));
    expect(selected, isNull);
    await tap(find.text('25'));
    expect(selected, DateTime.utc(2026, 7, 25));
    expect(tester.takeException(), isNull);
  });
}
