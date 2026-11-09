package dsa;

import java.util.HashSet;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public class Duplicate {
    public boolean hasDuplicate(int[] nums) {
        HashSet<Integer> set = new HashSet<>(IntStream.of(nums).boxed().collect(Collectors.toSet()));
        return nums.length == set.size();
    }
}