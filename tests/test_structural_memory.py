import unittest

from pete_discovery.fieldmap import DynamicFieldmap


class StructuralReactionMemoryTests(unittest.TestCase):
    def test_input_is_not_stored_as_data_but_its_structural_reaction_is(self):
        field = DynamicFieldmap()
        before = field.structure_hash
        reaction = field.observe_pair((0, 0, 1), (0, 1, 1), 9, accepted=False)
        self.assertNotEqual(before, field.structure_hash)
        self.assertIn("input_reference", reaction)
        self.assertNotIn("input", reaction)
        self.assertIn("gap_signature", reaction)
        self.assertTrue(reaction["gap_signature"]["prediction_mismatch"])
        self.assertNotEqual(reaction["transition"]["before"], reaction["transition"]["after"])
        self.assertTrue(reaction["mutations"])
        self.assertNotIn("a", field.samples[0])
        self.assertNotIn("b", field.samples[0])

    def test_retrieval_resonates_with_prior_gap_shape(self):
        field = DynamicFieldmap()
        a, b = (0, 0, 1), (0, 4, 1)
        self.assertEqual(field.retrieve_by_gap(a, b, 9, observed_conflict=True), [])
        field.observe_pair(a, b, 9, accepted=False)
        recalled = field.retrieve_by_gap(a, b, 9, observed_conflict=True)
        self.assertTrue(recalled)
        self.assertEqual(recalled[0]["score"], 1.0)
        self.assertEqual(recalled[0]["gap_signature"]["observation"], "conflict")

    def test_repeated_reactions_aggregate_instead_of_expanding_raw_memory(self):
        field = DynamicFieldmap()
        for _ in range(5):
            field.observe_pair((0, 0, 1), (0, 3, 1), 9, accepted=False)
        snapshot = field.snapshot()
        self.assertEqual(snapshot["reaction_events"], 5)
        self.assertEqual(snapshot["reaction_shapes"], 1)
        self.assertEqual(snapshot["recent_reactions"][0]["count"], 5)


if __name__ == "__main__":
    unittest.main()
