import treeData from "../data/tree.json" with { type: "json" };

type Leaf = "atasan" | "bawahan" | "fullbody" | "outer";

type TreeNode =
  | { feature: string; threshold: number; left: TreeNode; right: TreeNode }
  | { leaf: Leaf };

export interface TreeInput {
  body_shape_enc: number;
  gaya_bohemian: 0 | 1;
  gaya_casual: 0 | 1;
  gaya_classic: 0 | 1;
  gaya_formal: 0 | 1;
  gaya_sporty: 0 | 1;
}

const tree = treeData as TreeNode;

export function predict(input: TreeInput): Leaf {
  let node = tree;
  while (!("leaf" in node)) {
    const value = input[node.feature as keyof TreeInput];
    node = value <= node.threshold ? node.left : node.right;
  }
  return node.leaf;
}
