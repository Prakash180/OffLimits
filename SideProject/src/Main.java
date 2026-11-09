import dsa.Duplicate;
import dsa.MaxAvgSubarray;
import dsa.TwoSum;
import dsa.longestSubString;
import systemdesign.consistenthashing.ConsistentHashingDemo;
import systemdesign.messagequeue.MessageQueueDemo;

public class Main {
    public static void main(String[] args) throws InterruptedException {

        int[] nums = {1,12,-5,-6,50,3};
        int[] ans = new TwoSum().twoSum(nums, 6);
        boolean size = new Duplicate().hasDuplicate(nums);
//        System.out.println(size);
//      System.out.println(ans[0]+ "  " + ans[1]);
        String s = "tmmzuxt";
        String space = " ";
        System.out.println(space.length());
        int res = new longestSubString().lengthOfLongestSubstringOptimised(s);
        System.out.println(res);

        System.out.println("Max Avg = "+new MaxAvgSubarray().findMaxAverage(nums, 4));

        System.out.println("\n--- Consistent Hashing Demo ---");
        ConsistentHashingDemo.run();

        System.out.println("\n--- Message Queue Demo ---");
        MessageQueueDemo.run();
    }
}