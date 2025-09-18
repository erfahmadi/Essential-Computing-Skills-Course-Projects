#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/slab.h>
#include <linux/mutex.h>

#define DEVICE_NAME_READ  "lifo_read"
#define DEVICE_NAME_WRITE "lifo_write"
#define MAX_SIZE (1024 * 1024)

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Erfan Ahmadi");
MODULE_DESCRIPTION("A virtual LIFO");

static dev_t dev_number;
static struct cdev lifo_cdev;
static struct class *lifo_class;
static char *lifo_buffer;
static int lifo_top = 0;
static DEFINE_MUTEX(lifo_lock);

static ssize_t lifo_read(struct file *filp, char __user *buf, size_t count, loff_t *f_pos) {
    int to_copy, i;
    char *temp;
    ssize_t ret = 0;
    mutex_lock(&lifo_lock);
    if (lifo_top == 0) {
        mutex_unlock(&lifo_lock);
        return 0;
    }
    to_copy = min(count, (size_t)lifo_top);
    temp = kmalloc(to_copy, GFP_KERNEL);
    if (!temp) {
        mutex_unlock(&lifo_lock);
        return -ENOMEM;
    }
    for (i = 0; i < to_copy; i++) {
        temp[i] = lifo_buffer[lifo_top - 1 - i];
    }
    if (copy_to_user(buf, temp, to_copy)) {
        ret = -EFAULT;
    } else {
        lifo_top -= to_copy;
        ret = to_copy;
    }
    kfree(temp);
    mutex_unlock(&lifo_lock);
    return ret;
}

static ssize_t lifo_write(struct file *filp, const char __user *buf, size_t count, loff_t *f_pos) {
    ssize_t ret = 0;
    mutex_lock(&lifo_lock);
    if (lifo_top + count > MAX_SIZE) {
        ret = -ENOSPC;
    } else {
        if (copy_from_user(lifo_buffer + lifo_top, buf, count)) {
            ret = -EFAULT;
        } else {
            lifo_top += count;
            ret = count;
        }
    }
    mutex_unlock(&lifo_lock);
    return ret;
}

static int lifo_open(struct inode *inode, struct file *filp) {
    return 0;
}

static int lifo_release(struct inode *inode, struct file *filp) {
    return 0;
}

static struct file_operations fops_read = {
    .owner = THIS_MODULE,
    .read = lifo_read,
    .open = lifo_open,
    .release = lifo_release,
};

static struct file_operations fops_write = {
    .owner = THIS_MODULE,
    .write = lifo_write,
    .open = lifo_open,
    .release = lifo_release,
};

static int __init lifo_init(void) {
    int ret;
    struct cdev *write_cdev;
    ret = alloc_chrdev_region(&dev_number, 0, 2, "lifo_dev");
    if (ret < 0) {
        return ret;
    }
    lifo_buffer = kmalloc(MAX_SIZE, GFP_KERNEL);
    if (!lifo_buffer) {
        ret = -ENOMEM;
        goto fail_buffer;
    }
    lifo_class = class_create(THIS_MODULE, "lifo_class");
    if (IS_ERR(lifo_class)) {
        ret = PTR_ERR(lifo_class);
        goto fail_class;
    }
    cdev_init(&lifo_cdev, &fops_read);
    lifo_cdev.owner = THIS_MODULE;
    ret = cdev_add(&lifo_cdev, dev_number, 1);
    if (ret < 0) {
        goto fail_cdev;
    }
    device_create(lifo_class, NULL, MKDEV(MAJOR(dev_number), 0), NULL, DEVICE_NAME_READ);
    write_cdev = cdev_alloc();
    if (!write_cdev) {
        ret = -ENOMEM;
        goto fail_write_cdev;
    }
    cdev_init(write_cdev, &fops_write);
    write_cdev->owner = THIS_MODULE;
    ret = cdev_add(write_cdev, MKDEV(MAJOR(dev_number), 1), 1);
    if (ret < 0) {
        goto fail_write_add;
    }
    device_create(lifo_class, NULL, MKDEV(MAJOR(dev_number), 1), NULL, DEVICE_NAME_WRITE);
    printk(KERN_INFO "LIFO driver loaded (major=%d)\n", MAJOR(dev_number));
    return 0;

	fail_write_add:
		kfree(write_cdev);
	fail_write_cdev:
		cdev_del(&lifo_cdev);
	fail_cdev:
		class_destroy(lifo_class);
	fail_class:
		kfree(lifo_buffer);
	fail_buffer:
		unregister_chrdev_region(dev_number, 2);
    return ret;
}

static void __exit lifo_exit(void)
{
    device_destroy(lifo_class, MKDEV(MAJOR(dev_number), 0));
    device_destroy(lifo_class, MKDEV(MAJOR(dev_number), 1));
    class_destroy(lifo_class);
    cdev_del(&lifo_cdev);
    unregister_chrdev_region(dev_number, 2);
    kfree(lifo_buffer);
    printk(KERN_INFO "LIFO driver unloaded\n");
}

module_init(lifo_init);
module_exit(lifo_exit);
