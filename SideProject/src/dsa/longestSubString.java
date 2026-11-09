package dsa;

// 3. Longest Substring Without Repeating Characters

// Given a string s, find the length of the longest substring without duplicate characters.
// Input: s = "abcabcbb"
// Output: 3
// Explanation: The answer is "abc", with the length of 3. Note that "bca" and "cab" are also correct answers.

import java.util.HashMap;
import java.util.HashSet;
import java.util.Arrays;

public class longestSubString {
    public int lengthOfLongestSubstringBruteForce(String s) {
        int res = s != null && !s.isEmpty() ? 1 : 0;
        HashSet<Character> set = new HashSet<>();

        for (int i = 0; i < s.length(); i++) {
            set.clear();
            set.add(s.charAt(i));
            int j = i + 1;
            while (j < s.length()) {
                if (!set.contains(s.charAt(j))) {
                    set.add(s.charAt(j));
                    res = Math.max(res, set.size());
                    j++;
                } else {
                    break;
                }
            }
        }
        return res;
    }

    public int lengthOfLongestSubstringOptimised(String s) {
        if (s == null || s.length() == 0) return 0;

        HashMap<Character, Integer> map = new HashMap<>();
        int res = 0;
        int left = 0;

        for (int j = 0; j < s.length(); j++) {
            char c = s.charAt(j);
            if (map.containsKey(c)) {
                left = Math.max(left, map.get(c) + 1);
            }
            res = Math.max(res, j - left + 1);
            map.put(c, j);
        }

        return res;
    }

    public int lengthOfLongestSubstringWithoutMap(String s) {
        int[] last = new int[256];
        Arrays.fill(last, -1);
        int res = 0;
        int l = 0; // left of current window

        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            l = Math.max(l, last[c] + 1);
            res = Math.max(res, i - l + 1);
            last[c] = i;
        }

        return res;
    }

}