import 'package:flutter_test/flutter_test.dart';
import 'package:drugtime_mobile/features/adherence/domain/entities/adherence_history.dart';
import 'package:drugtime_mobile/features/adherence/domain/repositories/adherence_repository.dart';
import 'package:drugtime_mobile/features/adherence/presentation/state/adherence_controller.dart';

class RecordingRepository implements AdherenceRepository {
  late DateTime from;
  late DateTime to;
  @override
  Future<AdherenceHistory> fetch({required String patientId, required DateTime from, required DateTime to}) async {
    this.from = from;
    this.to = to;
    return AdherenceHistory(patientId: patientId, from: from, to: to, asOf: DateTime.utc(2026, 10, 29), summary: const AdherenceSummary(total: 0, taken: 0, late: 0, missed: 0, pending: 0, counted: 0, rate: null), groups: const []);
  }
}

void main() {
  test('reproduces inverted range after midnight at oldest month boundary', () async {
    var now = DateTime.utc(2026, 10, 28, 5);
    final repository = RecordingRepository();
    final controller = AdherenceController(repository, patientId: '11111111-1111-4111-8111-111111111111', now: () => now);
    try {
      expect(await controller.selectDate(DateTime.utc(2026, 7, 31)), isTrue);
      expect(repository.from, DateTime.utc(2026, 7, 31));
      now = DateTime.utc(2026, 10, 29, 5);
      await controller.refresh();
      expect(repository.from, DateTime.utc(2026, 8, 1));
      expect(repository.to, DateTime.utc(2026, 7, 31));
      expect(repository.from.isAfter(repository.to), isTrue);
    } finally { controller.dispose(); }
  });
}
